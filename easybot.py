import time
from rocketchat_py_sdk import driver as driver


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


bot = driver.Driver(url='localhost:3000', ssl=False, debug=True)
start(bot)
