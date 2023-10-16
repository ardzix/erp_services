
from django.contrib.auth.models import User
from .middleware import _thread_locals

# To use user authentication in the tests
def create_user(username="testuser", password="testpassword"):
    user =  User.objects.create_user(username=username, password=password)
    _thread_locals.user = user
    return user