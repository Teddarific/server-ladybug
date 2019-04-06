from bs4 import BeautifulSoup
import urllib.request
from urllib.parse import urlparse

def get_domain(URL):
    parsed_uri = urlparse(URL)
    result = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    return domain

def recieve_link(URL):
    response = urllib.request.urlopen(URL)
    print(response) # TOOD - error handling

    soup = BeautifulSoup(response, from_encoding=response.info().get_param('charset'), features="lxml")

    find_too_many_headers(soup)

    # find_bad_colors()

    # find_small_text()

    # find_light_text()

    # find_respsonsive()

def find_too_many_headers(soup):
    PRINT_NAME = "too many headers"
    TYPE = "too-many-headers"
    SEVERITY = "warning"
    my_print(PRINT_NAME)

    # code to find ...

# printName example: "small text", "too many headers"
def my_print(printName):
    print("Looking for " + str(printName) + "... ")

URL = "http://www.alexanderdanilowicz.com/"
recieve_link(URL)
