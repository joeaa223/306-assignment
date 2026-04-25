import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import api.v1.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'service_day_system.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            api.v1.routing.websocket_urlpatterns
        )
    ),
})
