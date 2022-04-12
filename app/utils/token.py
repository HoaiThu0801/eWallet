import datetime
import jwt
from .configKey import key as tokenKey
import app.services.accountService as Account
import app.services.merchantService as merchantService

def encodeIdToken(account_id):
    """
    Generates the Auth Token
    :return: string
    """
    account = Account.getOneAccount(account_id)
    if (account['accountType'] == 'merchant'):
        merchant = merchantService.getOneMerchant(account['merchantId'])
        key = merchant['apiKey']
    else:
        key = tokenKey

    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1, seconds=5),
            'iat': datetime.datetime.utcnow(),
            'sub': account_id
        }
        tokenencode = jwt.encode(
            payload,
            key,
            algorithm='HS256'
        )
        return tokenencode
    except Exception as e:
        return 404

def decodeIdToken(token):
    keyList = []
    keyList.append(tokenKey)
    merchantKeys = merchantService.getAllKeyMerchant()
    for item in merchantKeys:
       keyList.append(item['apiKey'])
    for key in keyList:
        try:
            payload = jwt.decode(token, key, algorithms=["HS256"])
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 403
        except jwt.InvalidTokenError:
            continue
    return 401     