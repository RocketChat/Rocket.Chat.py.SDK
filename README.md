# Rocket.Chat.py.SDK

Python DDP client for Rocket.Chat.

## Quick Start

Install the dependencies:

```
pip install -r requirements.txt
```

Run the bot.

```
python easybot.py
```

Say hello and the bot will answer you.

## Overview

This is a python SDK to make the access to Rocket.Chat easier.

## Docs

**TODO**

## Message Objects

The Rocket.Chat message schema can be found [here](https://rocket.chat/docs/developer-guides/schema-definition/).

## Driver Methods 

**TODO**

## Development

A local instance of Rocket.Chat is required for unit tests to confirm 
connection and subscription methods are functional. And it helps to manually 
run your SDK interactions (i.e. bots) locally while in development.

### Docker

Just run:

```
docker-compose up mongo rocketchat
```

* After that access `localhost:3000`

* Create the administrator user.

* Add the bot user with the necessary settings.
