import json
import uuid
import requests
from ..utils.configDB import connection
import app.services.accountService as Account

def createMerchantTable():
    conn = connection()
    cur = conn.cursor()
    try:
        cur.execute("""
                CREATE TABLE IF NOT EXISTS public.Merchant(
                merchantId UUID PRIMARY KEY,
                merchantName VARCHAR(200),
                merchantUrl VARCHAR(200) DEFAULT 'http://localhost:8080',
                apiKey UUID
            )
        """)
        conn.commit()
        print('create merchant table successfully')
    except Exception as e:
        print(f'Can\'t create merchant table, error: {e}')
    finally:
        cur.close()
def createMerchant(data):
    merchantName = str(data['merchantName'])
    merchantUrl = str(data['merchantUrl'])
    merchantId = str(uuid.uuid4())
    apiKey = str(uuid.uuid4())
    sql = f"""INSERT INTO public.merchant 
        (merchantId, merchantName, merchantUrl, apiKey)
        VALUES ('{merchantId}','{merchantName}','{merchantUrl}', '{apiKey}')"""
    conn = connection()
    try:
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        accountData = {
            'accountType': 'merchant',
            'merchantId' : merchantId
            }
        account = Account.createAccount(accountData)
        merchant = getOneMerchant(merchantId)
        return {
           "merchantName": merchant['merchantName'],
            "accountId": account['accountId'],
            "merchantId": merchant['merchantId'],
            "apiKey": merchant['apiKey'],
            "merchantUrl": merchant['merchantUrl']
        }
    except Exception as e:
        print("Can\'t create merchant, error: " + str(e))
    finally:
        if conn is not None:
            cur.close()
            conn.close()
def getOneMerchant(merchantId):
    conn = connection()
    sql = f"""SELECT * FROM public.merchant WHERE merchant.merchantId = '{merchantId}' """
    try:
        cur = conn.cursor()
        cur.execute(sql)
        data = cur.fetchone()
        return {
            "merchantId" : data[0],
            "merchantName" : data[1],
            "merchantUrl" : data[2],
            "apiKey" : data[3]
        }   
    except Exception as e:
        print("Can\'t get account, error: " + str(e))
    finally:
        if conn is not None:
            cur.close()
            conn.close()
def getAllKeyMerchant():
    conn = connection()
    sql = """ SELECT * FROM public.merchant """
    try:
        cur = conn.cursor()
        cur.execute(sql)
        data = cur.fetchall()
        merchants = []
        for item in data:
            merchants.append({
                "apiKey" : item[3]
            })
        return merchants
    except Exception as e:
        print("Can\'t create account, error: " + str(e))
    finally:
        if conn is not None:
            cur.close()
            conn.close()
def updateOrder(data,orderId):
    paymentStatus = str(data['paymentStatus'])
    url = f'http://127.0.0.1:5000/order/{orderId}'
    bodyData = {"payment_status" : paymentStatus}
    headers = {'content-type': 'application/json'}
    print(bodyData)
    response = requests.patch(url = url, data=json.dumps(bodyData), headers=headers)
    return response.status_code