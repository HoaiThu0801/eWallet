from datetime import datetime
from ..services.transactionService import getAllNotExpiredTransaction, updateTransaction
from ..services.merchantService import updateOrder

def checkTransactionExpire():
    transactions = getAllNotExpiredTransaction()
    if (len(transactions) <= 0):
        print('No expired transaction found')
        return
    for tran in transactions:
        tranDateTime= tran['createdAt']
        now = datetime.now()
        expiredTime = ((now - tranDateTime).total_seconds())/60
        if (expiredTime > 5):
            data = {}
            data['status'] = 'expired'
            data['transactionId'] = tran['transactionId']
            updateTransaction(data)
            dataOrder = {
                'paymentStatus' : 'expired'
            }
            updateOrder(dataOrder,  tran['extraData'])