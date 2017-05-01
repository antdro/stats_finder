# Python 3.6.0 |Anaconda 4.3.1 (64-bit)|

from importer import Request, urlopen, HTTPError, URLError, bs


def from_url_to_bs4(url):

    while True:
        req = Request(url)
        try:
            response = urlopen(req)
        except URLError as e:
            if hasattr(e, 'reason'):
                print('URLError. Failed to reach a server.')
                print('Reason: ', e.reason)
            elif hasattr(e, 'code'):
                print('URLError. The server couldn\'t fulfill the request.')
                print('Error code: ', e.code)
            continue
        except HTTPError as e:
            if hasattr(e, 'reason'):
                print('HTTPError. Reason: ', e.reason)
            elif hasattr(e, 'code'):
                print('HTTPError. Error code: ', e.code)
            continue
        break

    html_read = response.read()
    bs4 = bs(html_read, "lxml")

    return bs4