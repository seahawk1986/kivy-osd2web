from twisted.internet import protocol


class WebController(protocol.Protocol):
    def connectionMade(self):
        self.transport.write("SVDRP kivy-osd2web client; UTF-8\r\n")

    def dataReceived(self, data):
        data = data.decode('utf-8').strip()
        if data.lower() not in ('quit', 'exit'):
            response = []
            returncode, response = self.factory.app.handle_webctrl_message(data)
            if response:
                for line in response[:-1]:
                    self.transport.write("{}-{}\r\n".format(returncode, line))
                self.transport.write("{} {}\r\n".format(returncode, response[-1]))
        self.transport.write("221 kivy-osd2web closing connection\r\n")
        self.transport.loseConnection()


class WebControllerFactory(protocol.Factory):
    protocol = WebController

    def __init__(self, app):
        self.app = app

