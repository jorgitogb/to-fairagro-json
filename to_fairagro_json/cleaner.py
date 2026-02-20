import re
import html

class StringCleaner:
    @staticmethod
    def clean(s):
        """
        Unescapes HTML, strips tags, and normalizes special characters 
        to ASCII equivalents for better compatibility.
        """
        if not isinstance(s, str):
            return s
        
        # Unescape HTML entities
        s = html.unescape(s)
        # Strip HTML tags
        s = re.sub(r'<[^>]+>', '', s)
        
        # Normalization map
        replacements = {
            '\u2013': '-', # en-dash
            '\u2014': '--', # em-dash
            '\u2018': "'", # left single quote
            '\u2019': "'", # right single quote
            '\u201c': "'", # left double quote
            '\u201d': "'", # right double quote
            '\u00a0': ' ', # non-breaking space
            '\u00ae': '(R)', # registered trademark
            '\u2122': '(TM)', # trademark
            '\u00df': 'ss', # ß
            '\u00e4': 'ae', # ä
            '\u00f6': 'oe', # ö
            '\u00fc': 'ue', # ü
            '\u00c4': 'Ae', # Ä
            '\u00d6': 'Oe', # Ö
            '\u00dc': 'Ue', # Ü
            '"': "'",      # normalize double quotes to single
        }
        
        for old, new in replacements.items():
            s = s.replace(old, new)
            
        # Normalize whitespace (replace any whitespace combo with a single space)
        s = re.sub(r'\s+', ' ', s).strip()
        return s
