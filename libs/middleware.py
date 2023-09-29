from rest_framework.authentication import TokenAuthentication
import threading


_thread_locals = threading.local()

class SetCurrentUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.user = request.user
        response = self.get_response(request)
        return response


class CustomTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        user, token = super().authenticate_credentials(key)
        _thread_locals.user = user
        
        return user, token
