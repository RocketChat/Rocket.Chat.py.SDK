import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rocket.chat_py_sdk",
    version="0.0.1",
    author="Arthur Temporim",
    author_email="arthurrtl@gmail.com",
    description="A easy way to connect and interact with Rocket.Chat",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RocketChat/Rocket.Chat.py.SDK",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
