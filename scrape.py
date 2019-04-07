from bs4 import BeautifulSoup
# from spellchecker import SpellChecker
from urllib.parse import urlparse
import urllib.request
import cssutils
import requests
import logging
import re
import colorsys
import webcolors


PRODUCTION = False

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

def recieve_front_end_link(URL, socketio):
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
		find_too_many_h1s(soup, URL, socketio)
		find_inline_styles(soup, URL, socketio)
		find_broken_links(soup, URL, socketio)
		# this method loops through all the style sheets
		# it includes:
		#	find_small_text() - DONE
		# 	find_inaccessible_colors() - DONE
		# 	find_contrast_text() - WORKING ON
		#css_parse(soup, URL, socketio)
		# find_spelling_errors(soup, URL) - NEED THOMAS TO FIX IMPORT ERROR
		find_broken_buttons(soup, URL, socketio)
	#else:
		#css_parse(soup, URL, socketio)

	######### WORKING ON ############
	# find_respsonsive()

def css_parse(soup, URL, socketio):
	DOMAIN = get_domain(URL)
	cssLinkElements1 = soup.findAll("link", type="text/css")
	cssLinkElements2 = soup.findAll("link", rel="stylesheet")
	cssLinkLists = cssLinkElements1 + cssLinkElements2

	finalCSSLinks = []
	for cssLink in cssLinkLists:
		if "bootstrap" in str(cssLink) or "vendor" in str(cssLink) or "http" in str(cssLink):
			pass
		elif cssLink not in finalCSSLinks:
			finalCSSLinks.append(cssLink)

	first_bool = True
	smt_success_bool = True # assume successs
	inaccess_success_bool = True # assume success
	contrast_success_bool = True # assume success

	for item in finalCSSLinks:
		stylesheetName = item['href']
		create_print_json("css stylesheet: " + str(stylesheetName), socketio)
		fullCSSStyleLink = DOMAIN + item['href']
		cssutils.log.setLevel(logging.CRITICAL)
		sheet = cssutils.parseUrl(fullCSSStyleLink)

		for rule in sheet:
			if rule.type == rule.STYLE_RULE:
				contrast_bool = find_contrast(soup, URL, first_bool, stylesheetName, fullCSSStyleLink, rule, socketio)
				if contrast_bool == False:
					contrast_success_bool = False # once it turns false, it's not going back to True

				# HERE WE LOOP OVER THE PROPERTIES
				# THIS IS WHERE WE CALL ALL THE FUNCTIONS TO CHECK AT THE SAME TIME
				# SO WE ONLY HAVE TO LOOP OVER THE STYLE SHEET ONCE
				for cssProperty in rule.style:
					smt_bool = find_small_text(soup, URL, cssProperty, first_bool, stylesheetName, fullCSSStyleLink, rule, socketio)
					if smt_bool == False: # error
						smt_success_bool = False # once it turns false, it's not going back to True

					inaccess_bool = find_inaccessible_colors(soup, URL, cssProperty, first_bool, stylesheetName, fullCSSStyleLink, rule, socketio)
					if inaccess_bool == False:
						inaccess_success_bool = False # once it turns false, it's not going back to True

				first_bool = False

		if smt_success_bool: # if this stayed true the whole time it's a success
			create_success_json("small text", URL, socketio)

		if inaccess_success_bool:
			create_success_json("inaccessible colors", URL, socketio)
		else:
			TYPE = "inaccessible colors"
			SEVERITY = "warning"
			text = "We found " + str(len(INACCESSIBLE_COLORS_FOUND)) + " inaccessible colors."
			create_error_json(TYPE, SEVERITY, fullCSSStyleLink, text=text, meta=str(INACCESSIBLE_COLORS_FOUND), socketio=socketio)

		if contrast_success_bool:
			create_success_json("accessibility for colorblind users", URL, socketio)


def find_contrast(soup, URL, first_bool, stylesheetName, fullCSSStyleLink, rule, socketio):
	TYPE = "accessibility for colorblind users"
	SEVERITY = "warning"
	inaccessible_colors = []

	if first_bool:
		create_print_json(TYPE, socketio)

	cssString = rule.cssText
	
	# if (re.search('\scolor:', cssString) is not None) and "background-color:" in cssString:
	if rule.style['color'] and rule.style['background-color']:
		
		color = str(rule.style['color'])
		backgroundColor = str(rule.style['background-color'])

		# get them both in hex
		if color.startswith("#"):
			colorHex = color
		elif not color.startswith("rgb"):
			colorHex = webcolors.name_to_hex(color)
		else: # rgb
			colorHex = webcolors.rgb_to_hex(color)

		
		if backgroundColor.startswith("#"):
			backgroundHex = backgroundColor
		elif not backgroundColor.startswith("rgb"):
			backgroundHex = webcolors.name_to_hex(backgroundColor)
		else:
			backgroundHex = webcolors.rgb_to_hex(backgroundColor)

		# now we have them both in hex
		print("---------")
		print(colorHex)
		print(backgroundHex)
		val = distinguish_hex(colorHex, backgroundHex)
		if val:
			print(val)
			return False
		else:
			return True


# searches for red, green
def find_inaccessible_colors(soup, URL, cssProperty, first_bool, stylesheetName, fullCSSStyleLink, rule, socketio):
	TYPE = "inaccessible colors"
	SEVERITY = "warning"
	inaccessible_colors = ["red", "green", "#ff0000", "#00ff00"]

	if first_bool:
		create_print_json(TYPE, socketio)

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
def find_small_text(soup, URL, cssProperty, first_bool, stylesheetName, fullCSSStyleLink, rule, socketio):
	MINIMUM_SIZE_FONT = 12
	TYPE = "small text"
	SEVERITY = "warning"

	if first_bool:
		create_print_json(TYPE, socketio)

	# if font-size and it's value is in pixels
	if cssProperty.name == "font-size" and str(cssProperty.value)[-2:] == "px": # last 2 characters
		# convert font size to ints
		size = int(str(cssProperty.value[:-2])) # everything except last 2 characters
		if size < MINIMUM_SIZE_FONT:
			text = "You have a font size of " + str(size) + "px on stylesheet: " + stylesheetName
			create_error_json(TYPE, SEVERITY, fullCSSStyleLink, text=text, meta=rule.cssText, socketio=socketio)
			return False # error found

def find_broken_links(soup, URL, socketio):
	TYPE = "possible broken link"
	SEVERITY = "error"
	DOMAIN = get_domain(URL)
	create_print_json(TYPE, socketio)

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
			create_print_json(text, socketio)
			if int(response.status_code) >= 301 and int(response.status_code) != 999:
				text = "You have a link which returned a bad " + str(response.status_code) + " response code."
				create_error_json(TYPE, SEVERITY, URL, text=text, meta=htmlAnchor, socketio=socketio)

def find_too_many_h1s(soup, URL, socketio):
	TYPE = "too many header elements"
	SEVERITY = "warning"
	create_print_json(TYPE, socketio)

	h1TagsList = soup.find_all('h1')

	if len(h1TagsList) > 1:
		meta = h1TagsList
		text = "You have " + str(len(h1TagsList)) + " h1 elements on " + str(URL)
		create_error_json(TYPE, SEVERITY, URL, text=text, meta=meta, socketio=socketio)
	else:
		create_success_json(TYPE, URL, socketio)

# severity types: warning, error
def create_error_json(type, severity, URL, socketio, lineNumber=-1, text="", meta=""):
	json = {"type": type, "severity": severity, "URL": URL, "lineNumber": lineNumber, "text": text, "meta": str(meta)}
	print(json)
	if PRODUCTION:
		socketio.emit('data', json)
	return json

# severity types: info
def create_print_json(TYPE, socketio):
	json = {"severity": "info", "text": ("Running analysis of " + str(TYPE) + "... ")}
	print(json)
	if PRODUCTION:
		socketio.emit('data', json)
	return json

# severity type: success
def create_success_json(TYPE, URL, socketio):
	json = {"severity": "success", "URL": URL, "type": str(TYPE), "text": "Success, " + (str(TYPE)) + " test passed!"}
	print(json)
	if PRODUCTION:
		socketio.emit('data', json)
	return json


def find_inline_styles(soup, URL, socketio):
	TYPE = 'inline_styles'
	SEVERITY = 'warning'

	create_print_json(TYPE, socketio)

	error_list =  soup.find_all(style=True)
	if len(error_list) == 0:
		create_success_json(TYPE, URL, socketio)
	else:
		for error in error_list:
			text = "You have an inline styled elements on " + str(URL)
			create_error_json(TYPE, SEVERITY, URL, text=text, meta=error, socketio=socketio)

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
		create_success_json(TYPE, URL)

def find_broken_buttons(soup, URL, socketio):
	TYPE = 'broken_button'
	SEVERITY = 'warning'
	create_print_json(TYPE, socketio)
	broken_button = False

	button_href = soup.find_all('button', {"href": False})
	if len(button_href) != 0:
		text = "You have a button without an href at " + str(URL)
		create_error_json(TYPE, SEVERITY, URL, text=text, meta=button_href, socketio=socketio)
		broken_button = True

	for tag in soup.find_all('button'):
		for broken_tag in tag.findAll('a', {'href': False}):
			text = "You have a button without an href at " + str(URL)
			create_error_json(TYPE, SEVERITY, URL, text=text, meta=broken_tag, socketio=socketio)
			broken_button = True

	for tag in soup.find_all('div'):
		for broken_tag in tag.findAll('a', {'href': False}):
			text = "You have a button without an href at " + str(URL)
			create_error_json(TYPE, SEVERITY, URL, text=text, meta=broken_tag, socketio=socketio)
			broken_button = True

	for broken_tag in tag.findAll('a', {'href': False}):
		text = "You have a button without an href at " + str(URL)
		create_error_json(TYPE, SEVERITY, URL, text=text, meta=broken_tag, socketio=socketio)
		broken_button = True

	if not broken_button:
		create_success_json(TYPE, URL, socketio)

def rgb2hex(r, g, b):
	return '#%02x%02x%02x' % (r, g, b)

def hex2rgb(hex_str):
	m = re.match(
		r'^\#?([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})$', hex_str)
	return (int(m.group(1), 16), int(m.group(2), 16), int(m.group(3), 16))


def distinguish_hex(hex1, hex2, mindiff=50):
	"""
	Make sure two colors (specified as hex codes) are sufficiently different.
	Returns the two colors (possibly changed). mindiff is the minimal
	difference in lightness.

	RETURNS TRUE IF NO ISSUE
	RETURN CHANGED COLORS IF RECOMMENDATION TO CHANGE
	"""

	rgb1 = hex2rgb(hex1)
	rgb2 = hex2rgb(hex2)

	hls1 = colorsys.rgb_to_hls(*rgb1)
	hls2 = colorsys.rgb_to_hls(*rgb2)

	l1 = hls1[1]
	l2 = hls2[1]

	if abs(l1 - l2) >= mindiff:  # ok already
		return True

	restdiff = abs(l1 - l2) - mindiff
	if l1 >= l2:
		l1 = min(255, l1 + restdiff / 2)
		l2 = max(0, l1 - mindiff)
		l1 = min(255, l2 + mindiff)
	else:
		l2 = min(255, l2 + restdiff / 2)
		l1 = max(0, l2 - mindiff)
		l2 = min(255, l1 + mindiff)

	hsl1 = (hls1[0], l1, hls1[2])
	hsl2 = (hls2[0], l2, hls2[2])

	rgb1 = colorsys.hls_to_rgb(*hsl1)
	rgb2 = colorsys.hls_to_rgb(*hsl2)

	print(rgb1)
	print(rgb2)
	#return (rgb2hex(*rgb1), rgb2hex(*rgb2))
		
######## DRIVER ############
if __name__ == "__main__":
	FRONT_END_URL = "https://www.alexanderdanilowicz.com"
	recieve_front_end_link(FRONT_END_URL, "DEBUG_SOCKET")
