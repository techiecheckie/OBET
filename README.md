A website in Python using Flask.

The dependencies needed are:
flask-mongoengine
flask-wtf
flask
flask-bootstrap
flask-moment
flask-script
flask-mail
wtforms

Current issue is that the database can save and find properly through the command line,
but is having troubles from the front end.

To run this app:
$ python hello.py runserver

To test on the command line:
$ python hello.py shell
When using on the command line, the app, db, and User are already imported.
You must import anything else you would like to use.

The database is MongoDB and connects as a MongoEngine app.
MongoEngine does queries differently from MongoDB, but I believe
both types of queries can be done here.
