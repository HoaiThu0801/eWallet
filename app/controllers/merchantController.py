from ..services.merchantService import createMerchant, updateOrder

class MerchantController():
    def __init__(self):
        self.method = None
    def operation(self, token, data, param, query):
        if (self.method == 'GET'):
            pass
        if (self.method == 'POST'):
            return createMerchant(data)
class MerchantUpdateOrderController():
    def __init__(self):
        self.method = None
    def operation(self, token, data, param, query):
        if (self.method == 'GET'):
            pass
        if (self.method == 'POST'):
            return updateOrder(data, param)
        
