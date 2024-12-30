from backend.handler import lambda_handler
	
def test_endpoint(get_request):
	print(lambda_handler(event=get_request[0], context=get_request[1]))
