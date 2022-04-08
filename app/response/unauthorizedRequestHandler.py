from .requestHandler import RequestHandler

class UnauthorizedRequestHandler(RequestHandler):
    def __init__(self):
        super().__init__()
        self.contentType = 'application/json'
        self.contents = {
                "status" : 401,
                "message": "Unauthorized"
            }
        self.setStatus(401)