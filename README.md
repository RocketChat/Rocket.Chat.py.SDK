# Rocket.Chat.py.SDK

Python DDP client for Rocket.Chat.

## Quick Start

Install the dependencies in your virtualenv:

```sh
pip install -e .
```

Run the example bot.

```sh
python examples/bot.py
```

Say **hello** and the bot will answer you.

## Overview

This is a python SDK to make the access to Rocket.Chat easier, this package it's published [here](https://pypi.org/project/rocketchat-py-sdk/).

The main class of this package is the class `Driver`, to see it run in your terminal:

```python
$ python

>>> import rocketchat_py_sdk.driver as driver

>>> help(driver)

>>> bot = driver.Driver(url='localhost:3000', ssl=False)

>>> bot.connect()
```

## Docs

### Publish new version

* In your virtualenv:


```sh
python3 -m pip install --upgrade setuptools wheel

python3 setup.py sdist bdist_wheel

python3 -m pip install --upgrade twine

twine upload dist/*

```

## Message Objects

The Rocket.Chat message schema can be found [here](https://rocket.chat/docs/developer-guides/schema-definition/).

## Driver Methods 

**TODO**

## Development

A local instance of Rocket.Chat is required for unit tests to confirm 
connection and subscription methods are functional. And it helps to manually 
run your SDK interactions (i.e. bots) locally while in development.

In this repository have a **docker-compose** file that will help you to up
your own Rocket.Chat instance.

### Docker

Run this commands to start Rocket.Chat and database in background mode:

```sh
docker-compose up -d mongo

docker-compose up -d rocketchat
```

* After that access `localhost:3000`

* Create the administrator user.

* Add the bot user with the necessary settings see `easybot.py` to check
the `user` and `password`.
