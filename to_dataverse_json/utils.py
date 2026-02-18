def get_value(obj, key, default=''):
    """Helper to get value from entity, checking both short and expanded keys."""
    # Check direct key
    val = obj.get(key)
    # Check with schema.org prefix if not found
    if val is None:
        val = obj.get(f"https://schema.org/{key}")
        
    if val is None:
        return default
        
    if isinstance(val, list):
         if len(val) == 0: return default
         v = val[0]
         if isinstance(v, dict) and '@value' in v:
             return v['@value']
         if isinstance(v, dict) and 'value' in v:
             return v['value']
         return v
    return val

def resolve_entity(val, entities):
    """Resolves a value (which could be an ID, a dict with an ID, or a direct object)."""
    if isinstance(val, str):
        # Try to find in entities
        return next((ent for ent in entities if ent.get('id') == val or ent.get('@id') == val), val)
    if isinstance(val, dict) and 'id' in val:
         return next((ent for ent in entities if ent.get('id') == val['id'] or ent.get('@id') == val['id']), val)
    if isinstance(val, dict) and '@id' in val:
         return next((ent for ent in entities if ent.get('id') == val['@id'] or ent.get('@id') == val['@id']), val)
    return val
