import datetime
import time
import hashlib

from DDPClient import DDPClient
from pyee import EventEmitter


class MeteorClientException(Exception):
    """Custom Exception"""
    pass


class CollectionData(object):
    def __init__(self):
        self.data = {}

    def add_data(self, collection, id, fields):
        if collection not in self.data:
            self.data[collection] = {}
        if id not in self.data[collection]:
            self.data[collection][id] = {}
        for key, value in fields.items():
            self.data[collection][id][key] = value

    def change_data(self, collection, id, fields):
        if collection not in self.data:
            self.data[collection] = {}
        if id not in self.data[collection]:
            self.data[collection][id] = {}
        for key, value in fields.items():
            self.data[collection][id][key] = value

    def remove_data(self, collection, id):
        del self.data[collection][id]


class Driver(EventEmitter):
    def __init__(self, url, auto_reconnect=True,
                 auto_reconnect_timeout=0.5, debug=False, ssl=True):
        if ssl:
            protocol = 'wss://'
        else:
            protocol = 'ws://'

        url = protocol + url + '/websocket'
        EventEmitter.__init__(self)
        self.collection_data = CollectionData()
        self.ddp_client = DDPClient(
            url,
            auto_reconnect=auto_reconnect,
            auto_reconnect_timeout=auto_reconnect_timeout,
            debug=debug)
        self._prefixs = []
        self.debug = debug

        self.ddp_client.on('connected', self.connected)
        self.ddp_client.on('socket_closed', self.closed)
        self.ddp_client.on('failed', self.failed)
        self.ddp_client.on('added', self.added)
        self.ddp_client.on('changed', self.changed)
        self.ddp_client.on('removed', self.removed)
        self.ddp_client.on('reconnected', self._reconnected)
        self.connected = False
        self.subscriptions = {}
        self._login_data = None
        self._login_token = None

    def connect(self):
        """Connect to the meteor server"""
        self.ddp_client.connect()
        if(self.debug):
            print("[+] rocketchat: connected")

    def close(self):
        """Close connection with meteor server"""
        self.ddp_client.close()
        if(self.debug):
            print(
                '[-] rocketchat: connection closed: %s (%d)' %
                (reason, code))

    def _reconnected(self):
        """Reconnect
        Currently we get a new session every time so we have
        to clear all the data an resubscribe"""

        if self._login_data or self._login_token:

            def reconnect_login_callback(error, result):
                if error:
                    if self._login_token:
                        self._login_token = None
                        self._login(self._login_data,
                                    callback=reconnect_login_callback)
                        return
                    else:
                        raise MeteorClientException(
                            'Failed to re-authenticate during reconnect')

                self.connected = True
                self._resubscribe()

            if self._login_token:
                self._resume(self._login_token,
                             callback=reconnect_login_callback)
            else:
                self._login(self._login_data,
                            callback=reconnect_login_callback)
        else:
            self._resubscribe()

    def _resubscribe(self):
        self.collection_data.data = {}
        cur_subs = self.subscriptions.items()
        self.subscriptions = {}
        for name, value in cur_subs:
            self.subscribe(name, value['params'])
        self.emit('reconnected')

    #
    # Event Handlers
    #
    def connected(self):
        self.connected = True
        self.emit('connected')

    def closed(self, code, reason):
        self.connected = False
        self.emit('closed', code, reason)

    def failed(self, data):
        self.emit('failed', str(data))
        if(self.debug):
            print('[-] %s' % str(data))

    def added(self, collection, id, fields):
        self.collection_data.add_data(collection, id, fields)
        self.emit('added', collection, id, fields)
        if(self.debug):
            print('[+] added %s: %s' % (collection, id))

    def changed(self, collection, id, fields, cleared):
        print('[+] changed: %s %s' % (collection, id))

        if not fields.get('args'):
            return

        args = fields['args']

        if args[0] == "GENERAL":
            print("[+] message: general, skipping")
            return

        if args[0].get('msg'):
            return self.incoming(args[0])

        if args[0].get('attachments'):
            return self.downloading(args[0])
        self.collection_data.change_data(collection, id, fields)
        self.emit('changed', collection, id, fields)
        #self.collection_data.change_data(collection, id, fields, cleared)
        #self.emit('changed', collection, id, fields, cleared)

    def removed(self, collection, id):
        self.collection_data.remove_data(collection, id)
        self.emit('removed', collection, id)

    #
    # Account Management
    #
    def _resume(self, token, callback=None):
        login_data = {'resume': token}
        self._login(login_data, callback=callback)

    def _login(self, login_data, callback=None):
        self.emit('logging_in')

        def logged_in(error, data):
            if error:
                if self._login_token:
                    self._login_token = None
                    self._login(self._login_data, callback=callback)
                    return
                if callback:
                    callback(error, None)
                return

            self._login_token = data['token']

            if callback:
                callback(None, data)
            self.emit('logged_in', data)
            if(self.debug):
                print('[+] rocketchat: logged in')
                print(data)

        self.ddp_client.call('login', [login_data], callback=logged_in)

    def login(self, user, password, token=None, callback=None):
        """Login with a username and password
        Arguments:
        user - username or email address
        password - the password for the account
        Keyword Arguments:
        token - meteor resume token
        callback - callback function containing error as first argument and login data"""
        # TODO: keep the tokenExpires around so we know the next time
        #       we need to authenticate

        # encode the password
        password = password.encode('utf-8')
        # hash the password
        hashed = hashlib.sha256(password).hexdigest()
        # handle username or email address
        if '@' in user:
            user_object = {
                'email': user
            }
        else:
            user_object = {
                'username': user
            }
        password_object = {
            'algorithm': 'sha-256',
            'digest': hashed
        }

        self._login_token = token
        self._login_data = {'user': user_object, 'password': password_object}

        if token:
            self._resume(token, callback=callback)
        else:
            self._login(self._login_data, callback=callback)

    def logout(self, callback=None):
        """Logout a user
        Keyword Arguments:
        callback - callback function called when the user has been logged out"""
        self.ddp_client.call('logout', [], callback=callback)
        self.emit('logged_out')

    #
    # Meteor Method Call
    #
    def call(self, method, params, callback=None):
        """Call a remote method
        Arguments:
        method - remote method name
        params - remote method parameters
        Keyword Arguments:
        callback - callback function containing return data"""
        self._wait_for_connect()
        self.ddp_client.call(method, params, callback=callback)

    #
    # Subscription Management
    #
    def subscribe_to_messages(self):
        self.subscribe('stream-room-messages',
                       ['__my_messages__', False], self.cb1)

    def subscribe(self, name='stream-room-messages',
                  params=['__my_messages__'], callback=None):
        """Subscribe to a collection
        Arguments:
        name - the name of the publication
        params - the subscription parameters
        Keyword Arguments:
        callback - a function callback that returns an error (if exists)"""
        self._wait_for_connect()

        def subscribed(error, sub_id):
            if error:
                self._remove_sub_by_id(sub_id)
                if callback:
                    callback(error.get('reason'))
                return
            if callback:
                callback(None)
            self.emit('subscribed', name)

        if name in self.subscriptions:
            raise MeteorClientException('Already subcribed to {}'.format(name))

        sub_id = self.ddp_client.subscribe(name, params, subscribed)
        self.subscriptions[name] = {
            'id': sub_id,
            'params': params
        }

    def unsubscribe(self, name):
        """Unsubscribe from a collection
        Arguments:
        name - the name of the publication"""
        self._wait_for_connect()
        if name not in self.subscriptions:
            raise MeteorClientException('No subscription for {}'.format(name))
        self.ddp_client.unsubscribe(self.subscriptions[name]['id'])
        del self.subscriptions[name]
        self.emit('unsubscribed', name)

    def react_to_messages():
        """
        TODO
        """
        pass

    def respod_to_messages():
        """
        TODO
        """
        pass

    def async_call():
        """
        TODO
        """
        pass

    def cache_call():
        """
        TODO
        """
        pass

    def call_method():
        """
        TODO
        """
        pass

    def use_log():
        """
        TODO
        """
        pass

    def get_room_id():
        """
        TODO
        """
        pass

    def get_room_name():
        """
        TODO
        """
        pass

    def get_direct_message_room_id():
        """
        TODO
        """
        pass

    def join_room():
        """
        TODO
        """
        pass

    def prepare_message():
        """
        TODO
        """
        pass

    def send_message(self, id, message):
        self.call('sendMessage', [{'msg': message, 'rid': id}], self.cb)

    def send_to_room_id():
        """
        TODO
        """
        pass

    def send_to_room():
        """
        TODO
        """
        pass

    def send_direct_to_user():
        """
        TODO
        """
        pass

    #
    # Collection Management
    #
    def find(self, collection, selector={}):
        """Find data in a collection
        Arguments:
        collection - collection to search
        Keyword Arguments:
        selector - the query (default returns all items in a collection)"""
        results = []
        for _id, doc in self.collection_data.data.get(collection, {}).items():
            doc.update({'_id': _id})
            if selector == {}:
                results.append(doc)
            for key, value in selector.items():
                if key in doc and doc[key] == value:
                    results.append(doc)
        return results

    def find_one(self, collection, selector={}):
        """Return one item from a collection
        Arguments:
        collection - collection to search
        Keyword Arguments:
        selector - the query (default returns first item found)"""
        for _id, doc in self.collection_data.data.get(collection, {}).items():
            doc.update({'_id': _id})
            if selector == {}:
                return doc
            for key, value in selector.items():
                if key in doc and doc[key] == value:
                    return doc
        return None

    def insert(self, collection, doc, callback=None):
        """Insert an item into a collection
        Arguments:
        collection - the collection to be modified
        doc - The document to insert. May not yet have an _id attribute,
        in which case Meteor will generate one for you.
        Keyword Arguments:
        callback - Optional. If present, called with an error object as the first argument and,
        if no error, the _id as the second."""
        self.call("/" + collection + "/insert", [doc], callback=callback)

    def update(self, collection, selector, modifier, callback=None):
        """Insert an item into a collection
        Arguments:
        collection - the collection to be modified
        selector - specifies which documents to modify
        modifier - Specifies how to modify the documents
        Keyword Arguments:
        callback - Optional. If present, called with an error object as the first argument and,
        if no error, the number of affected documents as the second."""
        self.call("/" + collection + "/update",
                  [selector, modifier], callback=callback)

    def remove(self, collection, selector, callback=None):
        """Remove an item from a collection
        Arguments:
        collection - the collection to be modified
        selector - Specifies which documents to remove
        Keyword Arguments:
        callback - Optional. If present, called with an error object as its argument."""
        self.call("/" + collection + "/remove", [selector], callback=callback)

    #
    # Helper functions
    #
    def _time_from_start(self, start):
        now = datetime.datetime.now()
        return now - start

    def _remove_sub_by_id(self, sub_id):
        for name, cur_sub_id in self.subscriptions.items():
            if cur_sub_id == sub_id:
                del self.subscriptions[name]

    def _wait_for_connect(self):
        start = datetime.datetime.now()
        while not self.connected and self._time_from_start(start).seconds < 5:
            time.sleep(0.1)

        if not self.connected:
            raise MeteorClientException(
                'Could not subscribe because a connection has not been established')

    #
    # Internal dispatcher
    #
    def incoming(self, data):
        #print("[+] Message from %s: %s" % (data['u']['username'], data['msg']))
        print("[+] Incoming Message")
        #self.sendMessage(data['rid'],  "I hear you")
        # print(data)
        # Check if message was sent by another user

        for prefix in self._prefixs:
            if data['msg'].startswith(prefix['prefix']):
                prefix['handler'](self, data)

    def downloading(self, data):
        print("[+] attachement from %s: %d files" %
              (data['u']['username'], len(data['attachments'])))

    #
    # Public initializers
    #
    def add_prefix_handler(self, prefix, handler):
        self._prefixs.append({'prefix': prefix, 'handler': handler})

    #
    # Internal callback handlers
    #
    def cb(self, error, data):
        if not error:
            if self.debug:
                print(data)
            return

        print('[-] callback error:')
        print(error)

    def cb1(self, data):
        if(data):
            if(len(data) > 0):
                print(data)
                self.incoming(data)
            else:
                print(data)
                print("[+] callback success")
