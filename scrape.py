from bs4 import BeautifulSoup
# from spellchecker import SpellChecker
from urllib.parse import urlparse
import urllib.request
import cssutils
import requests
import logging
import re

PRODUCTION = True

headers = {
	"user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36",
	"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
	"accept-encoding": "gzip, deflate, sdch, br"
}

INACCESSIBLE_COLORS_FOUND = []

# Example:
# response = requests.get(url, headers=headers)

def get_domain(URL):
	parsed_uri = urlparse(URL)
	result = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
	return result

def recieve_front_end_link(URL):
	try:
		response = requests.get(URL, headers=headers)
		print("Success! URL is valid.")
	except:
		print("Provided URL is invalid.")
		return

	resource = urllib.request.urlopen(URL)
	soup = BeautifulSoup(resource, from_encoding=resource.info().get_param('charset'), features="lxml")

	######## COMPLETED ############
	if PRODUCTION:
		find_too_many_h1s(soup, URL)
		find_inline_styles(soup, URL)
		find_broken_links(soup, URL)
		# this method loops through all the style sheets
		# it includes: 
		#	find_small_text() - DONE
		# 	find_inaccessible_colors() - DONE
		# 	find_contrast_text() - WORKING ON
		css_parse(soup, URL)
		# find_spelling_errors(soup, URL)
		find_broken_buttons(soup, URL)


	######### WORKING ON ############
	# css_parse(soup, URL)
	# find_respsonsive()

def css_parse(soup, URL):
	DOMAIN = get_domain(URL)
	cssLinkElements1 = soup.findAll("link", type="text/css")
	cssLinkElements2 = soup.findAll("link", rel="stylesheet")
	cssLinkLists = cssLinkElements1 + cssLinkElements2

	finalCSSLinks = []
	for cssLink in cssLinkLists:
		if "bootstrap" in str(cssLink) or "vendor" in str(cssLink) or "http" in str(cssLink):
			pass
		else:
			finalCSSLinks.append(cssLink)

	first_bool = True
	smt_success_bool = True # assume successs
	inaccess_success_bool = True # assume success
	contrast_success_bool = True # assume success

	for item in finalCSSLinks:
		stylesheetName = item['href']
		create_print_json("css stylesheet: " + str(stylesheetName))
		fullCSSStyleLink = DOMAIN + item['href']
		cssutils.log.setLevel(logging.CRITICAL)
		try:
			sheet = cssutils.parseUrl(fullCSSStyleLink)
			for rule in sheet:
				if rule.type == rule.STYLE_RULE:

					#contrast_bool = find_contrast(soup, URL, first_bool, stylesheetName, fullCSSStyleLink, rule)
					#if contrast_bool == False:
						#contrast_success_bool = False # once it turns false, it's not going back to True

					# HERE WE LOOP OVER THE PROPERTIES
					# THIS IS WHERE WE CALL ALL THE FUNCTIONS TO CHECK AT THE SAME TIME
					# SO WE ONLY HAVE TO LOOP OVER THE STYLE SHEET ONCE
					for cssProperty in rule.style:
						smt_bool = find_small_text(soup, URL, cssProperty, first_bool, stylesheetName, fullCSSStyleLink, rule)
						if smt_bool == False: # error
							smt_success_bool = False # once it turns false, it's not going back to True

						inaccess_bool = find_inaccessible_colors(soup, URL, cssProperty, first_bool, stylesheetName, fullCSSStyleLink, rule)
						if inaccess_bool == False:
							inaccess_success_bool = False # once it turns false, it's not going back to True

						first_bool = False 
		except:
			pass

		if smt_success_bool: # if this stayed true the whole time it's a success
			create_success_json("small text")
		
		if inaccess_success_bool:
			create_success_json("inaccessible colors")
		else:
			TYPE = "inaccessible colors"
			SEVERITY = "warning"
			text = "We found " + str(len(INACCESSIBLE_COLORS_FOUND)) + " inaccessible colors."
			create_error_json(TYPE, SEVERITY, fullCSSStyleLink, text=text, meta=str(INACCESSIBLE_COLORS_FOUND))

		if contrast_success_bool:
			create_success_json("accessibility for colorblind users")


def find_contrast(soup, URL, first_bool, stylesheetName, fullCSSStyleLink, rule):
	TYPE = "accessibility for colorblind users"
	SEVERITY = "warning"
	inaccessible_colors = []

	if first_bool: 
		create_print_json(TYPE)

	cssString = rule.cssText
	if (re.search('\scolor:', cssString) is not None) and "background-color:" in cssString:
		print(rule.cssText)

# searches for red, green
def find_inaccessible_colors(soup, URL, cssProperty, first_bool, stylesheetName, fullCSSStyleLink, rule):
	TYPE = "inaccessible colors"
	SEVERITY = "warning"
	inaccessible_colors = ["red", "green", "#ff0000", "#00ff00"]

	if first_bool: 
		create_print_json(TYPE)

	# if font-size and it's value is in pixels
	if cssProperty.name == "color":
		# convert font size to ints
		our_color_value = cssProperty.value
		if if_bad_color(str(our_color_value), inaccessible_colors, 1):
			if our_color_value not in INACCESSIBLE_COLORS_FOUND: # don't add duplicates
				INACCESSIBLE_COLORS_FOUND.append(str(our_color_value))
			return False # error found

def if_bad_color(color, bad_colors_list, issue):
	# this is not fast but whatever
	if color in bad_colors_list: # this is if we have standard color wording like "blue"
		return True
	# otherwise if a hexvalue
	elif color.startswith("#") and len(color) == 7:
		hexV = color[1:]
		if hexV in bad_colors_list:
			return True
		else: # convert the hex to rgb and let it be the final test
			rgbV = convert_hex_to_rgb(hexV)
			return test_if_bad_rgb(rgbV, issue)
	# otherwise it's an rgb
	elif color.startswith("rgb"):
		return test_if_bad_rgb(color, issue)
	else: # not inaccessible
		return False

# if issue: 1, find_inaccessible_colors
# if issue: 2, contrast color

def test_if_bad_rgb(rgb_string, issue):
	rgbTuple = eval((rgb_string[3:]))
	r = rgbTuple[0]
	g = rgbTuple[1]
	b = rgbTuple[2]

	# then we can't have too much green or too much red
	if issue == 1:
		MAX_BAD = 125
		MIN_OTHER = 90
		if g > MAX_BAD and r < MIN_OTHER and b < MIN_OTHER:
			return True
		elif r > MAX_BAD and g < MIN_OTHER and b < MIN_OTHER:
			return True

	return False

def convert_hex_to_rgb(h):
	rgbTuple = (tuple(int(h[i:i+2], 16) for i in (0, 2, 4)))
	return "rgb" + str(rgbTuple)

# loops over properties
def find_small_text(soup, URL, cssProperty, first_bool, stylesheetName, fullCSSStyleLink, rule):
	MINIMUM_SIZE_FONT = 12
	TYPE = "small text"
	SEVERITY = "warning"

	if first_bool:
		create_print_json(TYPE)

	# if font-size and it's value is in pixels
	if cssProperty.name == "font-size" and str(cssProperty.value)[-2:] == "px": # last 2 characters
		# convert font size to ints
		size = int(str(cssProperty.value[:-2])) # everything except last 2 characters
		if size < MINIMUM_SIZE_FONT:
			text = "You have a font size of " + str(size) + "px on stylesheet: " + stylesheetName
			create_error_json(TYPE, SEVERITY, fullCSSStyleLink, text=text, meta=rule.cssText)
			return False # error found

def find_broken_links(soup, URL):
	TYPE = "possible broken link"
	SEVERITY = "error"
	DOMAIN = get_domain(URL)
	create_print_json(TYPE)

	for htmlAnchor in soup.find_all('a'):
		link = htmlAnchor.get('href')
		if "mailto:" in link:
			pass
		else:
			try:
				response = requests.get(link, headers=headers)
			except: 
				link = DOMAIN + link
				response = requests.get(link, headers=headers)

			text = "link: " + link
			create_print_json(text)
			if int(response.status_code) >= 301 and int(response.status_code) != 999:
				text = "You have a link which returned a bad " + str(response.status_code) + " response code."
				create_error_json(TYPE, SEVERITY, URL, text=text, meta=htmlAnchor)

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


def find_inline_styles(soup, URL):
	TYPE = 'inline_styles'
	SEVERITY = 'warning'
	
	create_print_json(TYPE)

	error_list =  soup.find_all(style=True)
	if len(error_list) == 0:
		create_success_json(TYPE)
	else:
		for error in error_list: 
			text = "You have an inline styled elements on " + str(URL)
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

def find_broken_buttons(soup, URL):
	TYPE = 'broken_button'
	SEVERITY = 'warning'
	create_print_json(TYPE)
	broken_button = False

	button_href = soup.find_all('button', {"href": False})
	if len(button_href) != 0:
		text = "You have a button without an href at " + str(URL)
		create_error_json(TYPE, SEVERITY, URL, text=text, meta=button_href) 
		broken_button = True

	for tag in soup.find_all('button'):
		for broken_tag in tag.findAll('a', {'href': False}):
			text = "You have a button without an href at " + str(URL)
			create_error_json(TYPE, SEVERITY, URL, text=text, meta=broken_tag)
			broken_button = True

	for tag in soup.find_all('div'):
		for broken_tag in tag.findAll('a', {'href': False}):
			text = "You have a button without an href at " + str(URL)
			create_error_json(TYPE, SEVERITY, URL, text=text, meta=broken_tag)
			broken_button = True

	for broken_tag in tag.findAll('a', {'href': False}):
		text = "You have a button without an href at " + str(URL)
		create_error_json(TYPE, SEVERITY, URL, text=text, meta=broken_tag)
		broken_button = True
			
	if not broken_button:
		create_success_json(TYPE)

		

######## DRIVER ############
FRONT_END_URL = "https://www.alexanderdanilowicz.com"
recieve_front_end_link(FRONT_END_URL)
