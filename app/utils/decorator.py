from functools import wraps
import app.services.authService as auth

def tokenRequired(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        authToken = args[0]
        response = auth.getLoggedInAccount(authToken)
    
        if  response in [404, 401, 403]:
            return 401
        return f(*args, **kwargs)

    return decorated
def tokenIssuerRequired(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        authToken = args[0]
        response = auth.getLoggedInAccount(authToken)
        if response in [404, 401, 403] or response['accountType'] != 'issuer':
            return 401
        return f(*args, **kwargs)

    return decorated

def tokenMerchantRequired(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        authToken = args[0]
        response = auth.getLoggedInAccount(authToken)
        if response in [404, 401, 403] or response['accountType'] != 'merchant':
            return 401
        return f(*args, **kwargs)

    return decorated
def tokenPersonalRequired(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        authToken = args[0]
        response = auth.getLoggedInAccount(authToken)
        if response in [404, 401, 403] or response['accountType'] != 'personal':
            return 401
        return f(*args, **kwargs)

    return decorated