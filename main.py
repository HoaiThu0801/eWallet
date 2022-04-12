from http.server import HTTPServer
from app.server import MyServer
from apscheduler.schedulers.background import BackgroundScheduler
from app.utils.checkTransactionExpire import checkTransactionExpire

hostName = "localhost"
serverPort = 8000


if __name__ == "__main__":        

    scheduler = BackgroundScheduler()
    scheduler.add_job(checkTransactionExpire, 'interval', seconds=3)
    scheduler.start()

    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")