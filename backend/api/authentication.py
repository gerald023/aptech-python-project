from rest_framework.authentication  import TokenAuthentication as BaseTokenAuth

#this allows us to use bearer in the header when a request is sent instead of just token.


class TokenAuthentication(BaseTokenAuth):
    keyword = 'Bearer';