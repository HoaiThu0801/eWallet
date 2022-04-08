import hashlib
import requests
import json
import uuid
import app.services.authService as auth
from ..utils.configDB import connection
from ..response.badRequestHandler import BadRequestHandler
from ..utils.decorator import tokenMerchantRequired, tokenPersonalRequired
from ..services.accountService import updateBalanceAccount
from ..services.merchantService import getOneMerchant

def createTransactionTable():
    conn = connection()
    cur = conn.cursor()
    try:
        cur.execute("""
             CREATE TYPE transactionStatus AS ENUM ('initialized', 'confirmed', 'verified', 'canceled', 'expired', 'failed')
        """)
        cur.execute("""
                CREATE TABLE IF NOT EXISTS public.Transaction(
                transactionId UUID PRIMARY KEY,
                transactionStatus transactionStatus, 
                incomeAccount UUID,
                outcomeAccount UUID,
                amount FLOAT DEFAULT 0,
                extraData VARCHAR(200),
                signature UUID,
                merchantId UUID REFERENCES Merchant(merchantId),
                createdAt timestamp without time zone DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print('create transaction table successfully')
    except Exception as e:
        print(f'Can\'t create transaction table, error: {e}')
    finally:
        cur.close()

@tokenMerchantRequired
def createTransaction(token, data):
    accountMerchant = auth.getLoggedInAccount(token)
    if (accountMerchant == ()):
        return BadRequestHandler()
    merchantId = str(data['merchantId'])
    extraData = str(data['extraData'])
    amount = int(data['amount'])
    payloadTransaction = {"merchantId": merchantId, "amount": amount, "extraData": extraData}
    signature = hashlib.md5(json.dumps(payloadTransaction).encode('utf-8')).hexdigest()
    transactionId = str(uuid.uuid4())
    incomeAccount = accountMerchant['accountId']
    transactionStatus = 'initialized'

    conn = connection()
    sql = f"""INSERT INTO public.transaction 
            (transactionId, transactionStatus, incomeAccount, amount, 
            extraData, signature, merchantId)
            VALUES ('{transactionId}','{transactionStatus}','{incomeAccount}',{amount},
            '{extraData}','{signature}','{merchantId}')"""
    try:
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        transaction = getOneTransaction(transactionId)
        return transaction   
    except Exception as e:
        print("Can\'t create transaction, error: " + str(e))
    finally:
        if conn is not None:
            cur.close()
            conn.close()
@tokenPersonalRequired
def confirmTransaction (token, data):
    accountPersonal = auth.getLoggedInAccount(token)
    if (accountPersonal == ()):
        return BadRequestHandler()
    if (checkValidTransaction(str(data['transactionId']), accountPersonal['balance']) == False):
        data['outcomeAccount'] = accountPersonal['accountId']
        data['status'] = 'failed'
        transactionResponse = updateTransaction(data)
        if (transactionResponse):
            return {
                "message" : "failed. Balance is not enough"
            }
    else:
        data['outcomeAccount'] = accountPersonal['accountId']
        data['status'] = 'confirmed'
        transactionResponse = updateTransaction(data)
        if (transactionResponse):
            return {
                "code": "SUC",
                "message": "Update transaction successfully"
            }
    return BadRequestHandler()
@tokenPersonalRequired
def verifyTransaction (token, data):
    accountPersonal = auth.getLoggedInAccount(token)
    if (accountPersonal == ()):
        return BadRequestHandler()
    if (checkValidTransaction(str(data['transactionId']), accountPersonal['balance']) == False):
        data['outcomeAccount'] = accountPersonal['accountId']
        data['status'] = 'failed'
        transactionResponse = updateTransaction(data)
        if (transactionResponse):
            return {
                "message" : "failed. Balance is not enough"
        }
    else:
        data['status'] = 'verified'
        transactionResponse = updateTransaction(data)
        if (transactionResponse):
            balance = accountPersonal['balance'] - transactionResponse['amount']
            if (updateBalanceAccount(balance, accountPersonal['accountId']) == 200):
                return 'OK'
            else:
                data['status'] = 'failed'
                transactionResponse = updateTransaction(data)
                if (transactionResponse):
                    return {
                        "message" : "failed. Balance is not enough"
                }
    return BadRequestHandler()
@tokenPersonalRequired
def cancelTransaction(token, data):
    accountPersonal = auth.getLoggedInAccount(token)
    if (accountPersonal == ()):
        return BadRequestHandler()
    data['status'] = 'canceled'
    transactionResponse = updateTransaction(data)
    if (transactionResponse):
        return 'OK'
    return BadRequestHandler()
def updateTransaction(data):
    outcomeAccount = None
    if ('outcomeAccount' in data):
        outcomeAccount = str(data['outcomeAccount'])
    status = str(data['status'])
    transactionId = str(data['transactionId'])
    conn = connection()
    if (outcomeAccount != None):
        sql = f"""
            UPDATE public.transaction 
            SET outcomeAccount = '{outcomeAccount}', transactionStatus = '{status}'
            WHERE transaction.transactionId = '{transactionId}'
        """
    else:
        sql = f"""
            UPDATE public.transaction 
            SET transactionStatus = '{status}'
            WHERE transaction.transactionId = '{transactionId}'
        """
    try:
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        transaction = getOneTransaction(transactionId)
        merchant = getOneMerchant(transaction['merchantId'])
        if (merchant == ()):
            return BadRequestHandler()
        return transaction  
    except Exception as e:
        print("Can\'t update transaction, error: " + str(e))
    finally:
        if conn is not None:
            cur.close()
            conn.close()
def getOneTransaction(transactionId):
    conn = connection()
    sql = f"""SELECT * FROM public.transaction WHERE transaction.transactionId = '{transactionId}' """
    try:
        cur = conn.cursor()
        cur.execute(sql)
        data = cur.fetchone()
        if (data == ()):
            return data
        return {
            "transactionId" : data[0],
            "merchantId" : data[7],
            "transactionStatus" : data[1],
            "incomeAccount" : data[2],
            "outcomeAccount" : data[3],
            "amount" : data[4],
            "extraData" : data[5],
            "signature" : data[6],
        }   
    except Exception as e:
        print("Can\'t get transaction, error: " + str(e))
    finally:
        if conn is not None:
            cur.close()
            conn.close()
def checkValidTransaction(transactionId, balance):
    transaction = getOneTransaction(transactionId)
    if (transaction == ()):
        return False
    return balance >= transaction['amount'] 

# def updateOrderStatus(paymentStatus, orderId, merchantUrl):
#     print(merchantUrl)
#     url = f'{merchantUrl}{orderId}'
#     print(url)
#     bodyData ={ "paymentStatus" : paymentStatus}
#     headers = {'content-type': 'application/json'}
#     response = requests.patch(url = url, data=json.dumps(bodyData), headers=headers)
#     return response.status_code