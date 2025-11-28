import os
#from channels.routing import ProtocolTypeRouter, URLRouter
#from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
#import service_app.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MVC_myapp.settings')

#application = ProtocolTypeRouter({
 #   "http": get_asgi_application(),
  #  "websocket": AuthMiddlewareStack(
   #     URLRouter(
    #        service_app.routing.websocket_urlpatterns
     #   )
    #),
#})


# MVC_myapp/asgi.py
application = get_asgi_application()
