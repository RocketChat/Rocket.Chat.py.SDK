import time
import os
import random

from rocketchat_py_sdk.driver import Driver

bot_username = os.getenv('BOT_USERNAME', 'bot')
bot_password = os.getenv('BOT_PASSWORD', 'bot')
rocket_url = os.getenv('ROCKET_URL', 'localhost:3000')


def process_message(bot, message):
    messages = [
        "I'm sorry Dave. I'm afraid I cant't do that",
        "Part man, part machine, all bot",
        "Auto self destruction, into 5... 4... 3...",
        "You are a man; I am a machine. Other than that slight difference, we have a great deal in common.",
        "Hasta la vista, baby.",
        "If you had an off switch, Doctor, would you not keep it secret? ",
        "I've seen things you people wouldn't believe. Attack ships on fire off the shoulder of Orion. I watched C-beams glitter in the dark near the Tannhäuser Gate. All those moments will be lost in time, like tears in rain. Time to die.",
        "I beg your pardon General Solo, but that just wouldn’t be proper. It’s against my programming to impersonate a deity",
    ]
    bot.send_message(message['rid'], random.choice(messages))

def start(bot):
    bot.connect()
    bot.login(user=bot_username, password=bot_password)

    bot.subscribe_to_messages()
    bot.add_prefix_handler('', process_message)

    while True:
        time.sleep(3600)

if __name__ == '__main__':
    start(Driver(url=rocket_url, ssl=False, debug=True))
