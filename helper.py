# Python 3.6.0 |Anaconda 4.3.1 (64-bit)|

from urllib.parse import urlsplit, urlunsplit, quote

def encode_non_ascii_url(url):
    
    """
    Given url with non ascii chars, return encoded url
    """

    url_split_result = urlsplit(url)
    url_list = list(url_split_result)
    url_path = url_list[2]

    url_list[2] = quote(url_path)
    url = urlunsplit(url_list)
    
    return url



def encode_all_non_ascii_urls(links):
    
    """
    Encodes each link containing non ascii chars, returns updated dictionary.
    """
    
    encoded_links = []

    for week in links:
        for link in links[week]:

            try:
                link.encode('ascii')
                encoded_links.append(link)
            except UnicodeEncodeError:
                link = encode_non_ascii_url(link)
                encoded_links.append(link)
        links[week] = encoded_links

    return links
