from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import app.routing
import user.routing

print(app.routing.websocket_urlpatterns+ user.routing.websocket_urlpatterns)

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            app.routing.websocket_urlpatterns+ user.routing.websocket_urlpatterns
        )

    ),

})