#!/usr/bin/python

from rocketchat import RocketChatBot, RocketChatClient
bot = RocketChatBot('pybot','12345',server='localhost:3000',ssl=False)
def hello(bot, message):
    bot.sendMessage(message['rid'], "Hi there user, I'm a Python Bot!")
    bot.sendMessage(message['rid'], "at your service")

bot.addPrefixHandler('hello', hello)

bot.start()
