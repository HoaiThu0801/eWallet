import app.services.merchantService as merchantService
import app.services.accountService as accountService
import app.services.transactionService as transactionService
if (__name__ == '__main__'):
    merchantService.createMerchantTable()
    accountService.createAccountTable()
    transactionService.createTransactionTable()