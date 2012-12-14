# Tamari

A non PHP forum engine.  This will provide a RESTful API along with a packaged demo
frontend.  For more documentation, view the stuff in the /docs folder.

## Setup/usage

Was developed inside of a virtualenv so just need one of those:

    $ mkvirtualenv tamari
    $ cp tamari/settings.py_template tamari/settings.py
    $ pip install -r requirements.txt

Edit the tamari/settings.py file to make changes to how you want your application
to run (the file has comments to explain some stuff).  To run you can either run
`make serve` if you have makefile or just `python serve.py`.  To run the tests,
use `make test`.
