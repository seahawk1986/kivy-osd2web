import json
from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketClientFactory, \
                                       WebSocketClientProtocol
from twisted.internet.protocol import ReconnectingClientFactory

LOGIN = json.dumps(
        {
            'event': 'login',
            'object': {'type': 0}
        }).encode('utf-8')
LOGOUT = json.dumps(
        {
            'event': 'logout',
            'object': {}
        }).encode('utf-8')

class CustomWebsocketClientProtocol(WebSocketClientProtocol):
    connections = list()

    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))
        self.connections.append(self)
        self.factory.resetDelay()

    def onOpen(self):
       self.sendMessage(LOGIN)

    def onMessage(self, payload, isBinary):
        if isBinary:
            #print("Binary message received: {0} bytes".format(len(payload)))
            pass
        else:
            data = json.loads(payload.decode('utf-8'), strict=False)
            name = data['event']
            dat = data['object']
            self.app.update_data(name, dat)

    def onClose(self, wasClean, code, reason):
        self.connections.remove(self)
        try:
           self.sendMessage(LOGOUT)
        except Exception as e:
           print("failed to send LOGOUT:", e)
        print("connection closed")
        print(wasClean, code, reason)

    @classmethod
    def broadcast_message(cls, data):
        payload = json.dumps(data, ensure_ascii = False).encode('utf8')
        for c in set(cls.connections):
            reactor.callFromThread(cls.sendMessage, c, payload)


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
