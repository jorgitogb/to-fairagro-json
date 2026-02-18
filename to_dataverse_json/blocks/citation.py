from ..utils import get_value, resolve_entity

class CitationParser:
    @staticmethod
    def parse(entities):
        authors = []
        title = ""
        alt_titles = []
        description = ""
        license_val = ""

        # Identify Investigation/Root Dataset
        root = next((e for e in entities if get_value(e, 'additionalType') == 'Investigation'), None)
        if not root:
             root = next((e for e in entities if e.get('@id') == './' or e.get('id') == './'), None)
        if not root:
             root = next((e for e in entities if 'Dataset' in str(e.get('@type', ''))), None)
        
        contacts = []
        keywords = []
        other_ids = []
        publication_date = ""
        subjects = []

        alternative_url = ""
        funder_items = []

        if root:
            # ... existing root extractions ...
            title = get_value(root, 'name', title)
            description = get_value(root, 'description', description)
            license_val = get_value(root, 'license', license_val)
            publication_date = get_value(root, 'datePublished', publication_date)
            if not publication_date:
                publication_date = get_value(root, 'dateCreated', '')
            
            # Extract Alternative URL
            dist = root.get('distribution', [])
            if not isinstance(dist, list): dist = [dist]
            for d_ref in dist:
                d = resolve_entity(d_ref, entities)
                if isinstance(d, dict):
                    url = get_value(d, 'contentUrl')
                    if url: 
                        alternative_url = url
                        break

            # Extract Funder
            funding = root.get('funder', []) or root.get('funding', [])
            if not isinstance(funding, list): funding = [funding]
            for f_ref in funding:
                f_obj = resolve_entity(f_ref, entities)
                if isinstance(f_obj, dict):
                    f_name = get_value(f_obj, 'name')
                    if f_name:
                        funder_items.append({"grantNumberValue": {"value": f_name}})

            # Extract Keywords
            kw_val = root.get('keywords', [])
            if isinstance(kw_val, str): 
                keywords = [k.strip() for k in kw_val.split(',') if k.strip()]
            elif isinstance(kw_val, list): 
                keywords = kw_val

            # Extract Subjects from 'about'
            about_val = root.get('about', [])
            if not isinstance(about_val, list): about_val = [about_val]
            for ab_ref in about_val:
                ab = resolve_entity(ab_ref, entities)
                if isinstance(ab, dict):
                    ab_name = get_value(ab, 'name')
                    if ab_name: subjects.append(ab_name)
                    elif ab.get('@id') and 'AGRI' in str(ab.get('@id')):
                        subjects.append("Agricultural Sciences")

            # Extract Identifiers (DOI)
            id_val = root.get('identifier', [])
            if isinstance(id_val, str): id_val = [id_val]
            for id_item in id_val:
                if isinstance(id_item, str):
                    if 'doi:' in id_item.lower() or 'doi.org' in id_item.lower() or id_item.startswith('10.'):
                        other_ids.append({"otherIdValue": {"value": id_item}, "otherIdAgency": {"value": "DOI"}})
                    else:
                        other_ids.append({"otherIdValue": {"value": id_item}, "otherIdAgency": {"value": "Other"}})

            # Helper for name cleaning
            def clean_name(n):
                return n.strip().rstrip(',') if n else ""

            # Extract Contacts
            def extract_contact(obj):
                if not isinstance(obj, dict): return
                email = get_value(obj, 'email')
                name = get_value(obj, 'name')
                if not name:
                    gname = get_value(obj, 'givenName')
                    fname = get_value(obj, 'familyName')
                    if gname and fname: name = f"{fname}, {gname}"
                    elif gname: name = gname
                    elif fname: name = fname

                if email:
                    contacts.append({
                        "datasetContactName": {"value": clean_name(name) or "FAIRagro Support"},
                        "datasetContactEmail": {"value": email}
                    })
                # Check contactPoint
                cp = obj.get('contactPoint')
                if cp:
                    for cp_item in (cp if isinstance(cp, list) else [cp]):
                        extract_contact(resolve_entity(cp_item, entities))

            for contact_key in ['contactPoint', 'creator', 'author', 'publisher', 'sourceOrganization']:
                cp_root = root.get(contact_key, [])
                for cp_ref in (cp_root if isinstance(cp_root, list) else [cp_root]):
                    extract_contact(resolve_entity(cp_ref, entities))
        
        if not contacts:
            contacts = [{"datasetContactName": {"value": "FAIRagro Support"}, "datasetContactEmail": {"value": "support@fairagro.net"}}]

        # Deduplicate contacts
        unique_contacts = []
        seen_emails = set()
        for c in contacts:
            email = c['datasetContactEmail']['value']
            if email not in seen_emails:
                unique_contacts.append(c)
                seen_emails.add(email)

        for e in entities:
            etype = str(e.get('@type', e.get('type', '')))
            add_type = get_value(e, 'additionalType')
            
            if 'Dataset' in etype:
                if add_type in ['Study', 'Assay']:
                    name = get_value(e, 'name')
                    if name and name != title: alt_titles.append(name)

                for key in ['creator', 'author', 'sourceOrganization']:
                    creators = e.get(key, [])
                    if not isinstance(creators, list): creators = [creators]
                    
                    for c in creators:
                        c_obj = resolve_entity(c, entities)
                        if isinstance(c_obj, dict):
                            c_type = str(c_obj.get('@type', c_obj.get('type', '')))
                            if 'Person' in c_type or 'Organization' in c_type or 'ContactPoint' in c_type:
                                name = get_value(c_obj, 'name')
                                if not name:
                                    gname = get_value(c_obj, 'givenName')
                                    fname = get_value(c_obj, 'familyName')
                                    if gname and fname: name = f"{fname}, {gname}"
                                    elif gname: name = gname
                                    elif fname: name = fname
                                
                                affiliation = ""
                                aff_val = c_obj.get('affiliation')
                                if aff_val:
                                    aff_obj = resolve_entity(aff_val, entities)
                                    if isinstance(aff_obj, dict):
                                        affiliation = get_value(aff_obj, 'name')
                                    else:
                                        affiliation = str(aff_obj)

                                if name:
                                    authors.append({
                                        "authorName": {"value": name},
                                        "authorAffiliation": {"value": affiliation}
                                    })
                                
                                # Check contactPoint for possible person name if organization
                                if 'Organization' in c_type:
                                    cp = c_obj.get('contactPoint')
                                    if cp:
                                        for cp_item in (cp if isinstance(cp, list) else [cp]):
                                            cp_obj = resolve_entity(cp_item, entities)
                                            cp_name = get_value(cp_obj, 'name')
                                            if cp_name:
                                                 authors.append({
                                                    "authorName": {"value": cp_name},
                                                    "authorAffiliation": {"value": name}
                                                })

        unique_authors = []
        seen_author_pairs = set()
        for a in authors:
            name = a['authorName']['value'].strip().rstrip(',')
            aff = a['authorAffiliation']['value'].strip().rstrip(',')
            a['authorName']['value'] = name
            a['authorAffiliation']['value'] = aff
            pair = (name, aff)
            if pair not in seen_author_pairs:
                unique_authors.append(a)
                seen_author_pairs.add(pair)

        distributors = []
        # Extract Distributors from publisher
        if root:
            pub_root = root.get('publisher', [])
            for pr in (pub_root if isinstance(pub_root, list) else [pub_root]):
                p = resolve_entity(pr, entities)
                if isinstance(p, dict):
                    p_name = get_value(p, 'name')
                    if p_name:
                        distributors.append({
                            "distributorName": {"value": p_name},
                            "distributorAffiliation": {"value": ""}
                        })

        if not subjects: subjects = ["Agricultural Sciences"]
        unique_subjects = list(set(subjects))

        return {
            "displayName": "Citation Metadata",
            "fields": [
                {"titleValue": {"value": title}},
                {"alternativeTitle": {"value": " / ".join(alt_titles)} if alt_titles else {"value": ""}},
                {"author": unique_authors},
                {"datasetDescription": [{"descriptionValue": {"value": description}}]},
                {"subject": [{"value": s} for s in unique_subjects]},
                {"datasetContact": unique_contacts},
                {"keyword": [{"keywordValue": {"value": kw}} for kw in keywords]},
                {"otherId": other_ids},
                {"publicationDate": {"value": publication_date}},
                {"distributor": distributors},
                {"alternativeURL": {"value": alternative_url}},
                {"grantNumber": funder_items},
                {"license": {"value": str(license_val)}}
            ]
        }
