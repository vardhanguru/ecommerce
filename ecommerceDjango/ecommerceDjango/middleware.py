class ForceSessionCookieMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.session.session_key and 'sessionid' not in response.cookies:
            print(f"Middleware setting session cookie: sessionid={request.session.session_key}")
            response.set_cookie(
                key='sessionid',
                value=request.session.session_key,
                max_age=1209600,
                httponly=True,
                samesite='None',
                secure=False,
                path='/'
            )
        return response