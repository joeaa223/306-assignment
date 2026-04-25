import requests
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

# Mapping prefixes to corresponding microservices
SERVICE_MAP = {
    'users': 'http://127.0.0.1:8001/users',
    'ngo': 'http://127.0.0.1:8002/api/activities',
    'register': 'http://127.0.0.1:8003/api/registrations',
}

@csrf_exempt
def api_gateway(request, service_name=None, path=''):
    # If service_name is not provided, we infer it from the path
    if service_name is None:
        if 'activities' in request.path: service_name = 'ngo'
        elif 'users' in request.path: service_name = 'users'
        elif 'registrations' in request.path: service_name = 'register'

    if service_name not in SERVICE_MAP:
        return JsonResponse({'error': 'Service not found'}, status=404)

    # Base URL from our map
    base_url = SERVICE_MAP[service_name]

    # For transparent routes (like /users/register/), we want to hit the microservice's root + original path
    if service_name in request.path and 'gateway' not in request.path:
        # If it's a transparent route, the request.path is already what we need (e.g. /users/register/)
        # We just need to prepend the actual microservice origin (port)
        from urllib.parse import urlparse
        parsed = urlparse(base_url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        target_url = f"{origin}{request.path}"
    else:
        # Standard gateway route
        target_url = f"{base_url}/{path}" if path else f"{base_url}/"
    
    try:
        # Prepare headers - strip auth/session headers from the monolith
        # so microservices don't reject requests due to unrecognized cookies
        skip_headers = {'host', 'cookie', 'authorization', 'x-csrftoken'}
        headers = {k: v for k, v in request.headers.items() if k.lower() not in skip_headers}
        data = request.body

        # Make the request to the target microservice
        response = requests.request(
            method=request.method,
            url=target_url,
            headers=headers,
            data=data,
            params=request.GET,
            timeout=10
        )
        
        # Build the response strictly from the proxy logic
        proxy_response = HttpResponse(
            content=response.content,
            status=response.status_code,
            content_type=response.headers.get('Content-Type', 'application/json')
        )
        return proxy_response
        
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': 'Microservice is unavailable', 'details': str(e)}, status=503)
