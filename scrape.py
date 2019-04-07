from bs4 import BeautifulSoup
from spellchecker import SpellChecker
from urllib.parse import urlparse
import urllib.request
import cssutils
import requests
import logging
import re




headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "accept-encoding": "gzip, deflate, sdch, br"
}

# Example:
# response = requests.get(url, headers=headers)

def get_domain(URL):
    parsed_uri = urlparse(URL)
    result = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    return result

def recieve_link(URL):
    try:
        response = requests.get(URL, headers=headers)
        print("Success! URL is valid.")
    except:
        print("Provided URL is invalid.")
        return

    resource = urllib.request.urlopen(URL)
    soup = BeautifulSoup(resource, from_encoding=resource.info().get_param('charset'), features="lxml")
    soupStringList = convert_soup_to_str_list(soup)

    # find_too_many_h1s(soup, URL)

    # find_broken_links(soup, URL)

    # find_bad_colors()

    # find_small_text(soup, URL)

    # find_light_text()

    # find_respsonsive()
    # find_inline_styles(soup, URL)
    find_spelling_errors(soup, URL)

def find_broken_links(soup, URL):
    TYPE = "broken links"
    SEVERITY = "error"
    create_print_json(TYPE)

    for htmlAnchor in soup.find_all('a'):
        link = htmlAnchor.get('href')
        print(link)
        response = requests.get(link, headers=headers)
        print(response.status_code)

def find_too_many_h1s(soup, URL):
    TYPE = "too many header elements"
    SEVERITY = "warning"
    create_print_json(TYPE)

    h1TagsList = soup.find_all('h1')

    if len(h1TagsList) > 1:
        meta = h1TagsList
        text = "You have " + str(len(h1TagsList)) + " h1 elements on " + str(URL)
        create_error_json(TYPE, SEVERITY, URL, text=text, meta=meta)
    else:
        create_success_json(TYPE)

def find_small_text(soup, URL):
	MINIMUM_SIZE_FONT = 14
	TYPE = "small text"
	SEVERITY = "warning"
	DOMAIN = get_domain(URL)
	create_print_json(TYPE)

	cssLinkElements=soup.findAll("link", type="text/css")

	errorFound = False
	for item in cssLinkElements:
		stylesheetName = item['href']
		fullCSSStyleLink = DOMAIN + item['href']
		cssutils.log.setLevel(logging.CRITICAL)
		sheet = cssutils.parseUrl(fullCSSStyleLink)

		for rule in sheet:
			if rule.type == rule.STYLE_RULE:
				# find property
				for cssProperty in rule.style:
					if cssProperty.name == "font-size":
						if str(cssProperty.value)[-2:] == "px": # last 2 characters
							size = int(str(cssProperty.value[:-2])) # everything except last 2 characters
							if size < MINIMUM_SIZE_FONT:
								text = "You have a font size of " + str(size) + "px on stylesheet: " + stylesheetName
								create_error_json(TYPE, SEVERITY, URL, text=text)
								errorFound = True
	if not errorFound:
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

def find_spelling_errors(soup, URL):
    TYPE = 'spell_check'
    SEVERITY = 'warning'
    create_print_json(TYPE)

    [s.extract() for s in soup('script')]
    text = soup.get_text()
    text = re.sub(r'[\n]', '', text)
    spell = SpellChecker()
    with open('google-10000-english.txt', 'r') as read_file:
        word_set = { line.strip() for line in read_file }

    misspelled_word = False
    for word in text.split(' '):
        if word not in word_set:
            if word != '' and word[0] not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                correct_spelling = spell.correction(word) 
                if correct_spelling != word:
                    misspelled_word = True
                    text = "You have a misspelled word at " + str(URL)
                    create_error_json(TYPE, SEVERITY, URL, text=text, meta=word)
    if not misspelled_word:
        create_success_json(TYPE)

recieve_link(URL)
