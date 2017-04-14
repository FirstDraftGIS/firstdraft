from django.contrib.auth.models import AnonymousUser
from rest_framework.authentication import BaseAuthentication, SessionAuthentication 

"""
class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening
"""

class CsrfExemptSessionAuthentication(BaseAuthentication):

    def authenticate(self, request):
        return (AnonymousUser(), "token")

    def authenticate_header(self, request):
        pass
