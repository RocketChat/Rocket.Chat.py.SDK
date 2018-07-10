import time
import datetime

from rocketchatclient import RocketChatClient, CollectionData, MeteorClientException


class RocketChatBot():
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

        # registering internal handlers
        #self.client.on('changed', self._changed)

    """
    Internal events handlers
    """
    #def _changed(self, collection, mid, fields):
    #    print('[+] changed: %s %s' % (collection, mid))

    #    if not fields.get('args'):
    #        return

    #    args = fields['args']

    #    if args[0] == "GENERAL":
    #        print("[+] message: general, skipping")
    #        return

    #    if args[0].get('msg'):
    #        return self._incoming(args[0])

    #    if args[0].get('attachments'):
    #        return self._downloading(args[0])

    """
    Internal dispatcher
    """
    #def _incoming(self, data):
    #    print("[+] Message from %s: %s" % (data['u']['username'], data['msg']))
    #    print("[+] Incoming Message")
    #    #self.sendMessage(data['rid'],  "I hear you")
    #    # print(data)
    #    #Check if message was sent by another user

    #    for prefix in self._prefixs:
    #        if data['msg'].startswith(prefix['prefix']):
    #            prefix['handler'](self, data)

    #def _downloading(self, data):
    #    print("[+] attachement from %s: %d files" % (data['u']['username'], len(data['attachments'])))

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

    #def addPrefixHandler(self, prefix, handler):
    #    self._prefixs.append({'prefix': prefix, 'handler': handler})

    #def sendMessage(self, id, message):
    #    self.client.call('sendMessage', [{'msg': message, 'rid': id}], self.cb)

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
        if(len(data)>0):
            print(data)
            self._incoming(data)
        else:
            print("[+] callback success")

