import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
import moments.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moment_project.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            moments.routing.websocket_urlpatterns
        )
    ),
})
