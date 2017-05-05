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
