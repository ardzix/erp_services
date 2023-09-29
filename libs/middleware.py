from rest_framework.authentication import TokenAuthentication
import threading

_thread_locals = threading.local()

class SetCurrentUserMiddleware:
    """
    Middleware to set the current user in thread-local storage.
    
    This middleware extracts the user from the request object 
    and sets it into thread-local storage. This allows other parts 
    of the application to access the current user outside of views 
    and without passing the request object.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        Set the current user from the request into thread-local storage.
        
        Args:
        - request (HttpRequest): The request object for this view.

        Returns:
        HttpResponse: The response object for this view.
        """
        _thread_locals.user = request.user
        return self.get_response(request)


class CustomTokenAuthentication(TokenAuthentication):
    """
    Custom Token Authentication to set the authenticated user 
    into thread-local storage.
    
    This extends the standard TokenAuthentication of the DRF 
    to extract the authenticated user from the token and sets it 
    into thread-local storage, ensuring applications can access 
    the user even outside the request-response lifecycle.
    """

    def authenticate_credentials(self, key):
        """
        Authenticate the token and set the user into thread-local storage.

        Args:
        - key (str): The token key.

        Returns:
        tuple: A tuple containing user and token.
        """
        user, token = super().authenticate_credentials(key)
        _thread_locals.user = user
        return user, token
