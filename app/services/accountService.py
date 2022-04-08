import uuid
import app.services.authService as auth
from ..utils.configDB import connection
from ..utils.token import encodeIdToken
from ..response.badRequestHandler import BadRequestHandler
from ..response.unauthorizedRequestHandler import UnauthorizedRequestHandler
from ..utils.decorator import tokenIssuerRequired

def createAccountTable():
    conn = connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            CREATE TYPE accountType AS ENUM ('merchant', 'personal', 'issuer')
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS public.Account(
                accountId UUID PRIMARY KEY,
                accountType accountType,
                balance FLOAT DEFAULT 0,
                merchantId UUID REFERENCES Merchant(merchantId)
            )
        """)
        conn.commit()
        print('create account table successfully')
    except Exception as e:
        print(f'Can\'t create account table, error: {e}')
    finally:
        cur.close()
def createAccount(data):
    accountType = str(data['accountType'])
    accountId = str(uuid.uuid4())
    conn = connection()
    if 'merchantId' in data:
        merchantId = str(data['merchantId'])
        sql = f"""INSERT INTO public.account 
        (accountId, accountType, merchantId)
        VALUES ('{accountId}','{accountType}','{merchantId}')"""
    else:
        sql = f"""INSERT INTO public.account 
            (accountId, accountType)
            VALUES ('{accountId}','{accountType}')"""
    try:
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        account = getOneAccount(accountId)
        return account   
    except Exception as e:
        print("Can\'t create account, error: " + str(e))
        return 404
    finally:
        if conn is not None:
            cur.close()
            conn.close()
@tokenIssuerRequired
def updateAccount(token, data, accountId):
    balance = int(data['amount'])
    accountIdPersonal = str(data['accountId'])
    issuer = auth.getLoggedInAccount(token)
    if (issuer['accountId'] != accountId):
        return UnauthorizedRequestHandler()
    accountPersonal = getOneAccount(accountIdPersonal)
    if (accountPersonal == ()):
        return BadRequestHandler()
    balance += accountPersonal['balance']
    conn = connection()
    sql = f"""
        UPDATE public.account 
        SET balance = {balance}
        WHERE account.accountId = '{accountIdPersonal}'
    """
    try:
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        return 'OK'
    except Exception as e:
        print("Can\'t get account, error: " + str(e))
        return 404
    finally:
        if conn is not None:
            cur.close()
            conn.close()
def updateBalanceAccount(balance, accountId):
    account = getOneAccount(accountId)
    conn = connection()
    sql = f"""
        UPDATE public.account 
        SET balance = {balance}
        WHERE account.accountId = '{accountId}'
    """
    try:
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        return 200
    except Exception as e:
        print("Can\'t update account, error: " + str(e))
        return 400
    finally:
        if conn is not None:
            cur.close()
            conn.close()
def getOneAccount(accountId):
    conn = connection()
    sql = f"""SELECT * FROM public.account WHERE account.accountId = '{accountId}' """
    try:
        cur = conn.cursor()
        cur.execute(sql)
        data = cur.fetchone()
        if (data == ()):
            return data
        return {
            "accountId" : data[0],
            "accountType" : data[1],
            "balance" : data[2],
            "merchantId" : data[3]
        }   
    except Exception as e:
        print("Can\'t get account, error: " + str(e))
        return 404
    finally:
        if conn is not None:
            cur.close()
            conn.close()
def checkBalance(accountId, amount):
    account = getOneAccount(accountId)
    return account['balance'] >= amount
def getToken(accountId):
    account = getOneAccount(accountId)
    if (account == ()):
        return 404
    return encodeIdToken(accountId)

