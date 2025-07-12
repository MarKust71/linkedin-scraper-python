# contact_utils.py
from typing import List, Dict, Any


def parse_contact_info_sections(contact_info_sections: List, full_name: str, classes) -> Dict[str, Any]:
    """
    Parsuje listę sekcji kontaktowych i zwraca:
      - contact_info: słownik z kluczami 'profile', 'phone', 'website', 'email', 'address', 'connected_on', 'birthday
    """
    CLASS_CONTACT_INFO_BIRTHDAY, CLASS_CONTACT_INFO_WEBSITE, CLASS_CONTACT_INFO_PHONE, CLASS_CONTACT_INFO_IM = (
        classes["CLASS_CONTACT_INFO_BIRTHDAY"],
        classes["CLASS_CONTACT_INFO_WEBSITE"],
        classes["CLASS_CONTACT_INFO_PHONE"],
        classes["CLASS_CONTACT_INFO_IM"]
    )

    extractors = {
        'Profile':   ('profile',        lambda sec: sec.find('a').text.strip()),
        'Phone':     ('phone',          lambda sec: [
                                            num.strip()
                                            for span in sec.find_all("span", class_=CLASS_CONTACT_INFO_PHONE)
                                            for num in span.text.splitlines()
                                            if num.strip()
                                        ]),
        'Website':   ('website',        lambda sec: [
                                            a.get("href", "").strip()
                                            for a in sec.find_all("a", class_=CLASS_CONTACT_INFO_WEBSITE)
                                            if a.get("href")
                                        ]),
        'Email':     ('email',          lambda sec: sec.find('a').text.strip()),
        'Address':   ('address',        lambda sec: sec.find('a').text.strip()),
        'Connected': ('connected_on',   lambda sec: sec.find('span').text.strip()),
        'Birthday':  ('birthday',       lambda sec:
                                            sec.find('span', class_=CLASS_CONTACT_INFO_BIRTHDAY).text.strip()
                      ),
        'IM':        ('im',             lambda sec: [
                                            ' '.join(span.text.strip() for span in li.find_all('span'))
                                            for li in sec.find_all("li", class_=CLASS_CONTACT_INFO_IM)
                                            if li.find_all('span')
                                        ]),
    }

    contact_info: Dict[str, Any] = {}
    unhandled: List[str] = []

    for section in contact_info_sections:
        header = section.find('h3').text.strip()
        if "Profile" in header:
            header = 'Profile'
        if "Websites" in header:
            header = 'Website'

        if header in extractors:
            key, extractor = extractors[header]
            try:
                value = extractor(section)
            except Exception as e:
                # w razie błędu ekstrakcji, zachowaj pustą wartość
                value = ''
                print(f'Warning {full_name}: nie udało się wyciągnąć ' + header + ':', e)
            contact_info[key] = value
        else:
            unhandled.append(header)

    if len(unhandled) > 0:
        contact_info['unhandled'] = unhandled

    return contact_info
