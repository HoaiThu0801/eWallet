from ..controllers.accountController import AccountController, TopUpAccountController
from ..controllers.merchantController import MerchantController, MerchantUpdateOrderController
from ..controllers.tokenController import TokenController
from ..controllers.transactionController import TransactionController, TransactionConfirmController, TransactionVerifyController, TransactionCancelController

routes = {
  "/" : "Hello World",
  "/account": AccountController(),
  "/account/{accountId}/token": TokenController(),
  "/account/{accountId}/topup": TopUpAccountController(),
  "/merchant" : MerchantController(),
  "/merchant/order/{orderId}" : MerchantUpdateOrderController(),
  "/transaction/create" : TransactionController(),
  "/transaction/confirm" : TransactionConfirmController(),
  "/transaction/verify" : TransactionVerifyController(),
  "/transaction/cancel" : TransactionCancelController()
}