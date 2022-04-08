from ..services.accountService import createAccount, updateAccount
class AccountController():
    def __init__(self):
        self.method = None
    def operation(self, token, data, param, query):
        if (self.method == 'GET'):
            pass
        if (self.method == 'POST'):
            return createAccount(data)
        
class TopUpAccountController():
    def __init__(self):
        self.method = None
    def operation(self, token, data, param, query):
        if (self.method == 'GET'):
            pass
        if (self.method == 'POST'):
            return updateAccount(token, data, param)
        