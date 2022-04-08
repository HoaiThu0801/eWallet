from functools import wraps
import app.services.authService as auth
from ..response.unauthorizedRequestHandler import UnauthorizedRequestHandler

def tokenRequired(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        authToken = args[0]
        response = auth.getLoggedInAccount(authToken)
    
        if response == None:
            return UnauthorizedRequestHandler()
        return f(*args, **kwargs)

    return decorated
def tokenIssuerRequired(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        authToken = args[0]
        response = auth.getLoggedInAccount(authToken)
        if response == None or response['accountType'] != 'issuer':
            return UnauthorizedRequestHandler()
        return f(*args, **kwargs)

    return decorated

def tokenMerchantRequired(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        authToken = args[0]
        response = auth.getLoggedInAccount(authToken)
        if response == None or response['accountType'] != 'merchant':
            return UnauthorizedRequestHandler()
        return f(*args, **kwargs)

    return decorated
def tokenPersonalRequired(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        authToken = args[0]
        response = auth.getLoggedInAccount(authToken)
        if response == None or response['accountType'] != 'personal':
            return UnauthorizedRequestHandler()
        return f(*args, **kwargs)

    return decorated