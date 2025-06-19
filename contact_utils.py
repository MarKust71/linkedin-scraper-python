# contact_utils.py
from typing import List, Dict, Any

CLASS_CONTACT_INFO_BIRTHDAY = "IAMzsKXcnLODYWqCzxgiQWMZrhvsEFipg t-14 t-black t-normal"
CALSS_CONTACT_INFO_WEBSITE = "pv-contact-info__contact-link link-without-visited-state"
CALSS_CONTACT_INFO_PHONE = "t-14 t-black t-normal"

def parse_contact_info_sections(contact_info_sections: List) -> Dict[str, Any]:
    """
    Parsuje listę sekcji kontaktowych i zwraca:
      - contact_info: słownik z kluczami 'profile', 'phone', 'email', 'address', 'connected_on'
    """
    extractors = {
        'Profile':   ('profile',      lambda sec: sec.find('a').text.strip()),
        'Phone':     ('phone',        lambda sec: sec.find(
            'span', class_=CALSS_CONTACT_INFO_PHONE).text.strip().split('\n')),
        'Website':   ('website',      lambda sec: sec.find(
            'a', class_=CALSS_CONTACT_INFO_WEBSITE)['href'].strip()),
        'Email':     ('email',        lambda sec: sec.find('a').text.strip()),
        'Address':   ('address',      lambda sec: sec.find('a').text.strip()),
        'Connected': ('connected_on', lambda sec: sec.find('span').text.strip()),
        'Birthday':  ('birthday',     lambda sec: sec.find(
            'span', class_=CLASS_CONTACT_INFO_BIRTHDAY).text.strip()),
    }

    contact_info: Dict[str, Any] = {}
    unhandled: List[str] = []

    for section in contact_info_sections:
        header = section.find('h3').text.strip()
        if "Profile" in header:
            header = 'Profile'

        if header in extractors:
            key, extractor = extractors[header]
            try:
                value = extractor(section)
            except Exception as e:
                # w razie błędu ekstrakcji, zachowaj pustą wartość
                value = ''
                print('Warning: nie udało się wyciągnąć ' + header + ':', e)
            contact_info[key] = value
        else:
            unhandled.append(header)

    if len(unhandled) > 0:
        contact_info['unhandled'] = unhandled

    return contact_info
