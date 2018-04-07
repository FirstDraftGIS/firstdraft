# https://django-rest-swagger.readthedocs.io/en/latest/settings/

# used by swagger to set login button destination
LOGIN_URL = 'rest_framework:login'
LOGOUT_URL = 'rest_framework:logout'

SHOW_REQUEST_HEADERS = True

SUPPORTED_SUBMIT_METHODS = ["get", "post"]