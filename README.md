# Tamari

A non PHP forum engine.  This is purely a backend with a nice RESTful API.

## Setup/usage

Was developed inside of a virtualenv so just need one of those:

    $ mkvirtualenv tamari
    $ pip install -r requirements.txt

Then you can run the unittest stuff with the test_tamari.py file or run a dev server
with runserver.py (this should work if you want to proxy it via a big kid prod type
web server, I use nginx).
