from bs4 import BeautifulSoup
import urllib.request

URL = "http://www.alexanderdanilowicz.com/"

def recieve_link(URL):
    response = urllib.request.urlopen(URL)
    print(response) # TOOD - error handling

    soup = BeautifulSoup(response, from_encoding=response.info().get_param('charset'), features="lxml")

    # find_bad_colors()

    # find_small_text()

    # find_light_text()

    # find_respsonsive()

recieve_link(URL)
