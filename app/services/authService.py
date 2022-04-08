from ..utils.token import decodeIdToken
import app.services.accountService as AccountService

def getLoggedInAccount(authToken):
    if (authToken):
        resp = decodeIdToken(authToken)
        account = AccountService.getOneAccount(resp)
        if account:
            return account
        return None
    return None