from ..services.transactionService import createTransaction, confirmTransaction, verifyTransaction, cancelTransaction
class TransactionController():
    def __init__(self):
        self.method = None
    def operation(self, token, data, param, query):
        if (self.method == 'GET'):
            pass
        if (self.method == 'POST'):
            return createTransaction(token, data)
class TransactionConfirmController():
    def __init__(self):
        self.method = None
    def operation(self, token, data, param, query):
        if (self.method == 'GET'):
            pass
        if (self.method == 'POST'):
            return confirmTransaction(token, data)
class TransactionVerifyController():
    def __init__(self):
        self.method = None
    def operation(self, token, data, param, query):
        if (self.method == 'GET'):
            pass
        if (self.method == 'POST'):
            return verifyTransaction(token, data)
class TransactionCancelController():
    def __init__(self):
        self.method = None
    def operation(self, token, data, param, query):
        if (self.method == 'GET'):
            pass
        if (self.method == 'POST'):
            return cancelTransaction(token, data)