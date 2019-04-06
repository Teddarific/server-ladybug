from bs4 import BeautifulSoup
import urllib.request
from urllib.parse import urlparse

URL = "http://www.alexanderdanilowicz.com/"

def get_domain(URL):
    parsed_uri = urlparse(URL)
    result = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    return domain

def recieve_link(URL):
    response = urllib.request.urlopen(URL)
    print(response) # TOOD - error handling

    soup = BeautifulSoup(response, from_encoding=response.info().get_param('charset'), features="lxml")

    # find_bad_colors()

    # find_small_text()

    # find_light_text()

    # find_respsonsive()

recieve_link(URL)
