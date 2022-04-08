import json
from .requestHandler import RequestHandler

class JsonHandler(RequestHandler):
    def __init__(self):
        super().__init__()
        self.contentType = 'application/json'

    def jsonParse(self, json_file):
        try:
            self.contents = json.dumps(json_file)
            self.setStatus(200)
            return True
        except:
            self.setStatus(404)
            return False