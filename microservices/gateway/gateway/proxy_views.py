import requests
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

SERVICES = {
    'users': 'http://localhost:8001',
    'ngos': 'http://localhost:8002',
    'registrations': 'http://localhost:8003',
}

@csrf_exempt
def gateway_proxy(request, service_name, path):
    """
    Lightweight API Gateway Proxy.
    Routes requests to internal microservices based on the service_name.
    """
    if service_name not in SERVICES:
        return JsonResponse({"error": "Service not found"}, status=404)

    target_url = f"{SERVICES[service_name]}/api/v1/{path}"
    
    # Forward the request (method, headers, body)
    headers = {k: v for k, v in request.headers.items() if k.lower() != 'host'}
    
    try:
        response = requests.request(
            method=request.method,
            url=target_url,
            headers=headers,
            data=request.body,
            params=request.GET,
            timeout=5.0
        )
        
        # Return the microservice's response back to the client
        django_response = HttpResponse(
            content=response.content,
            status=response.status_code,
            content_type=response.headers.get('Content-Type')
        )
        return django_response

    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": f"Gateway error: {str(e)}"}, status=502)
