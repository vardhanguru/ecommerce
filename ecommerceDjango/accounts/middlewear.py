class SessionHeaderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if hasattr(request, 'session') and hasattr(request.session, 'session_key') and request.session.session_key:
            response['X-Session-ID'] = request.session.session_key
        return response