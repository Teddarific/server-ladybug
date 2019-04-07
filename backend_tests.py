import requests

PRODUCTION = False

def recieve_link(URL):
	try:
		response = requests.get(URL)
		print("Success! URL is valid.")
	except:
		print("Provided URL is invalid.")
		return

	##### DELETE WHEN DONE TESTING #####
	test_response_time(URL)
	test_open_routes(URL)

	######## COMPLETED ############
	if PRODUCTION:
		test_open_routes(URL)
		test_response_time(URL)


	######### WORKING ON ############

def test_basic_passwords(URL):
	TYPE = "basic password security"
	SEVERITY = "error"
	#top 25 passwords 2018
	passwords = [
		"123456",
		"password",
		"123456789",
		"12345678",
		"12345",
		"111111",
		"1234567",
		"sunshine",
		"letmein",
		"qwerty",
		"iloveyou",
		"princess",
		"admin",
		"welcome",
		"666666",
		"abc123",
		"football",
		"123123",
		"monkey",
		"654321",
		"!@#$%^&*",
		"charlie",
		"hello",
		"whatever",
		"password1",
		"qwerty123",
		"aa123456",
		"master",
		"passw0rd",
		"login",
		"access",
		"baseball",
		"starwars",
		"qazwsx"
	]

	create_print_json(TYPE)



def test_response_time(URL):
	TYPE = "response time"
	SEVERITY = "info"
	create_print_json(TYPE)
	response_time = requests.get(URL).elapsed.total_seconds()
	print(response_time)
	#according to Google/speedtests
	if (response_time > 0.2):
		SEVERITY = "warning"
	create_error_json(TYPE, SEVERITY, URL, meta=response_time)


def test_open_routes(URL):
	api_route = ["/api/", "/" ]
	routes= [
	"main",
	"instance",
	"upload",
	"uploads",
	"metric",
	"metrics",
	"map",
	"maps",
	"users",
	"messages",
	"message",
	"help",
	"deals",
	"deal",
	"shop",
	"buy",
	"purchases",
	"cart",
	"shopping",
	"list",
	"all",
	"info",
	"information",
	"filter",
	"filters",
	"route",
	"routes",
	"router",
	"get",
	"put",
	"customers",
	"sellers",
	"sell",
	"items",
	"item",
	"graph",
	"graphs",
	"music",
	"artists",
	"artist",
	"songs",
	"song",
	"name",
	"users",
	"user",
	"charge",
	"receipts",
	"receipt",
	"signup",
	"signin",
	"auth",
	"authentication",
	"security",
	"safe",
	"secure",
	"service",
	"services",
	"search",
	"searches",
	"delete",
	"update",
	"find"
	]

	access_denied_codes = [400, 401, 403, 404]
	TYPE = "open routes"
	SEVERITY = "warning"
	create_print_json(TYPE)

	for route in routes:
		for api in api_route:
			test_route = URL + api + route
			response_get = requests.get(test_route)
			response_put = requests.put(test_route)
			if (response_get.status_code not in access_denied_codes):
				temp_meta = [test_route, "GET", response_get.status_code]
				create_error_json(TYPE, SEVERITY, URL, meta=temp_meta)
			if (response_put.status_code not in access_denied_codes):
				temp_meta = [test_route, "PUT", response_put.status_code]
				create_error_json(TYPE, SEVERITY, URL, meta=temp_meta)
				

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

######## DRIVER ############
URL = "https://dealio-cs98.herokuapp.com/api"
recieve_link(URL)