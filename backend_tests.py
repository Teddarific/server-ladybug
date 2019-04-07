import requests
import paramiko
from scrape import create_error_json, create_print_json, create_success_json

PRODUCTION = True

def recieve_back_end_link(URL, socketio):
	try:
		response = requests.get(URL)
		create_print_json("Confirmed valid API URL", socketio)
		print("Confirmed provided URL is valid.")
	except Exception as e:
		print(e)
		create_error_json("Provided invalid API URL", "error", URL, socketio=socketio, text="The provided API URL could not be successfully pinged", meta="")
		print("Provided URL is invalid.")
		return

	##### DELETE WHEN DONE TESTING #####

	test_basic_passwords(URL, socketio)

	######## COMPLETED ############
	if PRODUCTION:
		test_open_routes(URL, socketio)
		test_response_time(URL, socketio)

	socketio.emit('data', {"severity": "info", "type": "text", "text": "Completed testing."})

	######### WORKING ON ############

def test_basic_passwords(URL, socketio):
	TYPE = "basic password security"
	SEVERITY = "error"
	#top 25 passwords 2018
	PASSWORDS = [
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

	USERS = [
		"root",
		"admin",
		"Admin",
		"test",
		"guest",
		"info",
		"adm",
		"user",
		"administrator",
		"Administrator",
		"username",
		"user1",
		"pos",
		"demo",
	]

	create_print_json(TYPE, socketio)

	print(user_pw_combinations(USERS,PASSWORDS, URL, socketio))

def user_pw_combinations(USERS, PASSWORDS, URL, socketio):
	TYPE = "basic password security"
	SEVERITY = "error"
	for user in USERS:
		for password in PASSWORDS:
			print(user)
			print(password)
			try:
				client = paramiko.SSHClient()
				client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
				conn = client.connect(URL, username=user, password=password)
				if conn is None:
					create_error_json(TYPE, SEVERITY, URL, socketio=socketio, text="This API is vulnerable to ssh")
				client.close()
			except paramiko.AuthenticationException:
				output="Authentication Failed"
				create_success_json(TYPE, URL, socketio)
				print(output)
			except ConnectionResetError:
				create_success_json(TYPE, URL, socketio)
				print("reset")
				return ("good")
			except paramiko.ssh_exception.SSHException:
				create_success_json(TYPE, URL, socketio)
				print("ssh ecept")
				return ("good")
			except Exception:
				create_success_json(TYPE, URL, socketio)
				print("exception")
				return ("good")


def test_response_time(URL, socketio):
	TYPE = "response time"
	SEVERITY = "info"
	create_print_json(TYPE, socketio)
	response_time = requests.get(URL).elapsed.total_seconds()
	print(response_time)
	#according to Google/speedtests
	if (response_time > 0.2):
		SEVERITY = "warning"
		create_error_json(TYPE, SEVERITY, URL, meta=response_time, socketio=socketio, text="Response time is slower than typical standards")
	else:
		create_success_json(TYPE, URL, socketio)

def test_open_routes(URL, socketio):
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
	create_print_json(TYPE, socketio)

	for route in routes:
		for api in api_route:
			test_route = URL + api + route
			response_get = requests.get(test_route)
			response_put = requests.put(test_route)
			if (response_get.status_code not in access_denied_codes):
				temp_meta = [test_route, "GET", response_get.status_code]
				create_error_json(TYPE, SEVERITY, URL, meta=temp_meta, socketio=socketio, text="Discovered exposed API routes")
			if (response_put.status_code not in access_denied_codes):
				temp_meta = [test_route, "PUT", response_put.status_code]
				create_error_json(TYPE, SEVERITY, URL, meta=temp_meta, socketio=socketio, text="Discovered exposed API routes")

######## DRIVER ############
if __name__ == "__main__":
	URL = "https://dealio-cs98.herokuapp.com/api"
	recieve_back_end_link(URL)
