restful-todo-flask [![Build Status](https://travis-ci.com/adamj57/restful-todo-flask.svg?branch=master)](https://travis-ci.com/adamj57/restful-todo-flask)
==================

secrets.py
----------

If you want to run this on your machine, create `secrets.py`
 file containing `FLASK_SECRET` and `JWT_SECRET` global vars.
 These must contain secret keys - without them your instance **ISN'T SECURE.**
 
 
venv.sh
-------

If you want to automaticly install venv with all dependencies,
 simply run this file while being in main directory. It will create venv
 and install all required modules.