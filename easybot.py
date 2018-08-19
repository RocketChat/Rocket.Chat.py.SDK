import time

# import the local driver for tests
import sys
sys.path.append('src/rocketchat_py_sdk/')
from driver import Driver, CollectionData, MeteorClientException

# import the published package
#from rocketchat_py_sdk import driver as driver


def start(bot):
    bot.connect()
    bot.login(user='pybot', password='12345', callback=bot.cb)
    bot.subscribe_to_messages()

    def hello(bot, message):
        bot.send_message(message['rid'], "Hi there user, I'm a Python Bot!")
        bot.send_message(message['rid'], "at your service")

    bot.add_prefix_handler('hello', hello)

    # let's yeld to background task
    while True:
        time.sleep(3600)

# local driver call
bot = Driver(url='localhost:3000', ssl=False, debug=True)

# published package driver call
#bot = driver.Driver(url='localhost:3000', ssl=False, debug=True)
start(bot)
