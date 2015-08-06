A website in Python using Flask.

The dependencies needed are:
flask, 
flask-mongoengine, 
flask-wtf, 
flask-bootstrap, 
flask-moment, 
flask-script, 
flask-mail, 
wtforms

It's suggested that you install a virtual environment (virtualenv), and then install
all dependencies there.

Current issue is that the database can save and find properly through the command line,
but is having troubles from the front end.

To run this app (on Linux):
$ python hello.py runserver

To test on the command line (also on Linux):
$ python hello.py shell

When using on the command line, the app, db, and User are already imported.
You must import anything else you would like to use.

The database is MongoDB and connects as a MongoEngine app.

MongoEngine does queries differently from MongoDB, but I believe
both types of queries can be done here.
