# contact_utils.py
from typing import List, Tuple, Dict, Any
import pprint

def parse_contact_info_sections(contact_info_sections: List) -> Tuple[Dict[str, Any], List[str]]:
    """
    Parsuje listę sekcji kontaktowych i zwraca:
      - contact_info: słownik z kluczami 'profile', 'phone', 'email', 'address', 'connected_on'
      - unhandled: lista nagłówków, których nie obsłużyliśmy
    """
    extractors = {
        'Profile':   ('profile',     lambda sec: sec.find('a').text.strip()),
        'Phone':     ('phone',       lambda sec: sec.find(
            'span', class_='t-14 t-black t-normal').text.strip().split('\n')),
        'Website':   ('website',     lambda sec: sec.find(
            'a', class_='pv-contact-info__contact-link link-without-visited-state')['href'].strip()),
        'Email':     ('email',       lambda sec: sec.find('a').text.strip()),
        'Address':   ('address',     lambda sec: sec.find('a').text.strip()),
        'Connected': ('connected_on',lambda sec: sec.find('span').text.strip()),
    }

    contact_info: Dict[str, Any] = {}
    unhandled: List[str] = []

    for section in contact_info_sections:
        header = section.find('h3').text.strip()
        if header in extractors:
            key, extractor = extractors[header]
            try:
                value = extractor(section)
            except Exception as e:
                # w razie błędu ekstrakcji, zachowaj pustą wartość
                value = ''
                print('Warning: nie udało się wyciągnąć ' + header + ':', e)
            contact_info[key] = value
            pprint.pprint(key + ': ' + str(value))
        else:
            unhandled.append(header)

    pprint.pprint('Contact info: ' + str(contact_info))
    pprint.pprint('Unhandled sections: ' + str(unhandled))

    return contact_info, unhandled
