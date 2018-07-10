import time
from rocketchatclient import RocketChatClient, CollectionData, MeteorClientException


def start(bot):
    bot.connect()
    bot.subscribe_to_messages()
    bot.login(user='pybot', password='12345', callback=bot.cb)

    def hello(bot, message):
        bot.send_message(message['rid'], "Hi there user, I'm a Python Bot!")
        bot.send_message(message['rid'], "at your service")

    bot.addPrefixHandler('hello', hello)

    # let's yeld to background task
    while True:
        time.sleep(3600)


bot = RocketChatClient(url='localhost:3000', ssl=False, debug=True)
start(bot)
