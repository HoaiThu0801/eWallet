from ..services.accountService import getToken
class TokenController():
    def __init__(self):
        self.method = None
    def operation(self, token, data, param, query):
        if (self.method == 'GET'):
            return getToken(param)
        if (self.method == 'POST'):
            pass
        
