import json
from autobahn.twisted.websocket import WebSocketClientFactory, \
                                       WebSocketClientProtocol
from twisted.internet.protocol import ReconnectingClientFactory

LOGIN = json.dumps(
        {
            'event': 'login',
            'object': {'type': 1}
        }).encode('utf-8')
LOGOUT = json.dumps(
        {
            'event': 'logout',
            'object': {}
        }).encode('utf-8')

class CustomWebsocketClientProtocol(WebSocketClientProtocol):

   def onConnect(self, response):
       print("Server connected: {0}".format(response.peer))
       self.factory.resetDelay()

   def onOpen(self):
       self.sendMessage(LOGIN)

   def onClose(self):
       self.sendMessage(LOGOUT)

   def onMessage(self, payload, isBinary):
      if isBinary:
         #print("Binary message received: {0} bytes".format(len(payload)))
         pass
      else:
         data = json.loads(payload.decode('utf-8'))
         name = data['event']
         dat = data['object']
         self.app.update_data(name, dat)

   def onClose(self, wasClean, code, reason):
       print("connection closed")
       print(wasClean, code, reason)


class WSClientFactory(WebSocketClientFactory, ReconnectingClientFactory):

    protocol = CustomWebsocketClientProtocol

    def __init__(self, app, *args, **kwargs):
        self.app = app
        CustomWebsocketClientProtocol.app = self.app
        super(WSClientFactory, self).__init__(*args, **kwargs)

    def clientConnectionLost(self, connector, reason):
        print("connection lost", reason)
        self.retry(connector)

    def clientConnectionFailed(self, connector, reason):
        print("connection failed", reason)
        self.retry(connector)
