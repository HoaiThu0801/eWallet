from ..utils.token import decodeIdToken
import app.services.accountService as AccountService

def getLoggedInAccount(authToken):
    if (authToken):
        resp = decodeIdToken(authToken)
        if (resp != 403 and resp != 401):
            account = AccountService.getOneAccount(resp)
            if account:
                return account
            return 401
        return resp
    return 401