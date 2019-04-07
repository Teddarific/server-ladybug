from bs4 import BeautifulSoup
import urllib.request
from urllib.parse import urlparse


def get_domain(URL):
    parsed_uri = urlparse(URL)
    result = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    return domain

def recieve_link(URL):
    response = urllib.request.urlopen(URL)
    #print(response) # TOOD - error handling

    soup = BeautifulSoup(response, from_encoding=response.info().get_param('charset'), features="lxml")
    soupStringList = convert_soup_to_str_list(soup)

#    find_too_many_h1s(soup, URL)
    #find_too_many_headers(soup)

    # find_bad_colors()

    # find_small_text()

    # find_light_text()

    # find_respsonsive()
    find_inline_styles(soup, URL)

def find_too_many_h1s(soup, URL):
    TYPE = "too many header elements"
    SEVERITY = "warning"
    create_print_json(TYPE)
    h1TagsList = soup.find_all('h1')

    if len(h1TagsList) > 1:
        meta = h1TagsList
        text = "You have " + str(len(h1TagsList)) + " h1 elements on " + str(URL)
        create_error_json(TYPE, SEVERITY, URL, text=text, meta=meta)
    create_success_json(TYPE)

# severity types: warning, error
def create_error_json(type, severity, URL, lineNumber=-1, text="", meta=""):
    json = {"type": type, "severity": severity, "URL": URL, "lineNumber": lineNumber, "text": text, "meta": meta}
    print(json)
    return json

# severity types: info
def create_print_json(TYPE):
    json = {"severity": "info", "text": ("Running analysis of " + str(TYPE) + "... ")}
    print(json)
    return json

# severity type: success
def create_success_json(TYPE):
    json = {"severity": "success", "text": "Success, " + (str(TYPE)) + " test passed!"}
    print(json)
    return json

def convert_soup_to_str_list(soup):
    soupStringList = (str(soup).split("\n"))
    return soupStringList
    find_inline_styles(soup)

#def find_too_many_headers(soup):
#    PRINT_NAME = "too many headers"
#    TYPE = "too-many-headers"
#    SEVERITY = "warning"
#    my_print(PRINT_NAME)

    # code to find ...

# printName example: "small text", "too many headers"
def my_print(printName):
    print("Looking for " + str(printName) + "... ")

URL = "http://www.alexanderdanilowicz.com/"

def find_inline_styles(soup, URL):
    TYPE = 'inline_styles'
    SEVERITY = 'warning'
    
    create_print_json(TYPE)

    create_success_json(TYPE)
    error_list =  soup.find_all(style=True)
    if len(error_list) == 0:
        create_print_json(TYPE)
    else:
        for error in error_list: 
            text = "You have " + str(len(error_list)) + " inline styled elements on " + str(URL)
            create_error_json(TYPE, SEVERITY, URL, text=text, meta=error)


recieve_link(URL)
