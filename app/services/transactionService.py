import time
import hashlib
import requests
import json
import uuid
import app.services.authService as auth
from ..utils.configDB import connection
from ..response.badRequestHandler import BadRequestHandler
from ..utils.decorator import tokenMerchantRequired, tokenPersonalRequired
from ..services.accountService import updateBalanceAccount, getOneAccount
from ..services.merchantService import getOneMerchant, updateOrder
from ..utils.timeOut import timeout, TimeoutError

def createTransactionTable():
    conn = connection()
    cur = conn.cursor()
    try:
        cur.execute("""
             CREATE TYPE transactionStatus AS ENUM ('initialized', 'confirmed', 'verified', 'canceled', 'expired', 'failed', 'completed')
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
        conn.close()

@tokenMerchantRequired
def createTransaction(token, data):
    merchantId = str(data['merchantId'])
    extraData = str(data['extraData'])
    amount = int(data['amount'])
    payloadTransaction = {"merchantId": merchantId, "amount": amount, "extraData": extraData}
    signature = hashlib.md5(json.dumps(payloadTransaction).encode('utf-8')).hexdigest()
    transactionId = str(uuid.uuid4())

    accountMerchant = auth.getLoggedInAccount(token)
    if (accountMerchant == ()):
        return BadRequestHandler()

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
        return 404
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
        transaction = getOneTransaction(str(data['transactionId']))
        if (transaction['transactionStatus'] != 'initialized'):
            return 404
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
        transaction = getOneTransaction(str(data['transactionId']))
        if (transaction['transactionStatus'] != 'confirmed'):
            return 404
        data['status'] = 'completed'
        transactionResponse = updateTransaction(data)
        if (transactionResponse):
            balance = accountPersonal['balance'] - transactionResponse['amount']
            if (updateBalanceAccount(balance, accountPersonal['accountId']) == 200):
                accountMerchant = getOneAccount(transactionResponse['incomeAccount'])
                balanceMerchant = accountMerchant['balance'] + transactionResponse['amount']
                updateBalanceAccount(balanceMerchant, accountMerchant['accountId'])
                return 'OK'
            else:
                data['status'] = 'failed'
                transactionResponse = updateTransaction(data)
                if (transactionResponse):
                    return {
                        "message" : "failed. Balance is not enough"
                }
    return 404
@tokenPersonalRequired
def cancelTransaction(token, data):
    accountPersonal = auth.getLoggedInAccount(token)
    if (accountPersonal == ()):
        return 404
    transaction = getOneTransaction(str(data['transactionId']))
    if (transaction['transactionStatus'] != 'confirmed'):
        return 404
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
        dataOrder = {
                'paymentStatus' : status
        }
        updateOrder(dataOrder,  transaction['extraData'])
        if (merchant == ()):
            return 404
        return transaction  
    except Exception as e:
        print("Can\'t update transaction, error: " + str(e))
        return 404
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
        return 404
    finally:
        if conn is not None:
            cur.close()
            conn.close()
def getAllTransaction ():
    conn = connection()
    sql = """SELECT * FROM public.transaction"""
    try:
        cur = conn.cursor()
        cur.execute(sql)
        data = cur.fetchall()
        transactions = []
        for item in data:
            transactions.append({
                 "transactionId" : item[0],
                "merchantId" : item[7],
                "transactionStatus" : item[1],
                "incomeAccount" : item[2],
                "outcomeAccount" : item[3],
                "amount" : item[4],
                "extraItem" : item[5],
                "signature" : item[6],
            })
        return transactions
    except Exception as e:
        print("Can\'t get all  transaction, error: " + str(e))
        return 404
    finally:
        if conn is not None:
            cur.close()
            conn.close()
def getAllNotExpiredTransaction():
    conn = connection()
    sql = """SELECT * FROM public.transaction  
            where transactionStatus != 'canceled'  AND transactionStatus != 'completed' AND transactionStatus != 'expired'
        """
    try:
        cur = conn.cursor()
        cur.execute(sql)
        data = cur.fetchall()
        transactions = []
        for item in data:
            transactions.append({
                "transactionId" : item[0],
                "merchantId" : item[7],
                "transactionStatus" : item[1],
                "incomeAccount" : item[2],
                "outcomeAccount" : item[3],
                "amount" : item[4],
                "extraData" : item[5],
                "signature" : item[6],
                "createdAt": item[8]
            })
        return transactions
    except Exception as e:
        print("Can\'t get all  transaction, error: " + str(e))
        return 404
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