import time
from rocketchatclient import RocketChatClient, CollectionData, MeteorClientException

def start(bot):
    bot.connect()
    bot.subscribe('stream-room-messages', ['__my_messages__', False], bot.cb1)
    bot.login('pybot', '12345', callback=bot.cb)

    def hello(bot, message):
      bot.sendMessage(message['rid'], "Hi there user, I'm a Python Bot!")
      bot.sendMessage(message['rid'], "at your service")

    bot.addPrefixHandler('hello', hello)

    # let's yeld to background task
    while True:
        time.sleep(3600)

bot = RocketChatClient(url='localhost:3000',ssl=False, debug=True)
start(bot)

