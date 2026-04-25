from django.shortcuts import render

def error_404_view(request, exception):
    """Custom 404 handler"""
    return render(request, '404.html', status=404)

def error_500_view(request):
    """Custom 500 handler"""
    return render(request, '500.html', status=500)
