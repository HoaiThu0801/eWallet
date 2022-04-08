from app.services.merchantService import createMerchantTable
from app.services.accountService import createAccountTable
from app.services.transactionService import createTransactionTable

if (__name__ == '__main__'):
    createMerchantTable()
    createAccountTable()
    createTransactionTable()