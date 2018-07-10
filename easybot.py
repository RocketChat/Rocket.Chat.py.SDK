import time
import datetime

from rocketchatclient import RocketChatClient, CollectionData, MeteorClientException


class EasyBot():
    def __init__(self, user, password, server='open.rocket.chat', ssl=True):
        self.username = user
        self.password = password
        self.server = server
        self.debug = True

        #self._prefixs = []
        if ssl:
            protocol = 'wss://'
        else:
            protocol = 'ws://'
        self.client = RocketChatClient(protocol + server + '/websocket',debug=self.debug)

    """
    Public initializers
    """
    def start(self):
        self.client.connect()
        self.client.subscribe('stream-room-messages', ['__my_messages__', False], self.cb1)
        self.client.login(self.username, self.password.encode('utf-8'), callback=self.cb)

        def hello(bot, message):
          self.client.sendMessage(message['rid'], "Hi there user, I'm a Python Bot!")
          self.client.sendMessage(message['rid'], "at your service")

        self.client.addPrefixHandler('hello', hello)

        # let's yeld to background task
        while True:
            time.sleep(3600)

    """ 
    Internal callback handlers
    """
    def cb(self, error, data):
        if not error:
            if self.debug:
                print(data)
            return

        print('[-] callback error:')
        print(error)

    def cb1(self, data):
        # if not self.debug:
        #     return
        if(data):
          if(len(data)>0):
              print(data)
              self._incoming(data)
          else:
              print("[+] callback success")

bot = EasyBot('pybot','12345',server='localhost:3000',ssl=False)
bot.start()

