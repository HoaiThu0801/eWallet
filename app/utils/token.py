import datetime
import jwt
from .configKey import key as tokenKey
import app.services.accountService as Account
from ..services.merchantService import getOneMerchant, getAllKeyMerchant

def encodeIdToken(account_id):
    """
    Generates the Auth Token
    :return: string
    """
    account = Account.getOneAccount(account_id)
    print(account)
    if (account['accountType'] == 'merchant'):
        merchant = getOneMerchant(account['merchantId'])
        key = merchant['apiKey']
    else:
        key = tokenKey
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1, seconds=5),
            'iat': datetime.datetime.utcnow(),
            'sub': account_id
        }
        return jwt.encode(
            payload,
            key,
            algorithm='HS256'
        )
    except Exception as e:
        return e

def decodeIdToken(token):
    keyList = []
    keyList.append(tokenKey)
    merchantKeys = getAllKeyMerchant()
    for item in merchantKeys:
       keyList.append(item['apiKey'])
    for key in keyList:
        try:
            payload = jwt.decode(token, key, algorithms=["HS256"])
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please get new token.'
        except jwt.InvalidTokenError:
            continue
    return 'Invalid token. Please try other token again.'       