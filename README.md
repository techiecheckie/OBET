A website in Python using Flask.

It's suggested that you install a virtual environment (virtualenv), and then install
all dependencies there.

Current issue is that for some reason, the MAIL_USERNAME/PASSWORD variables cannot be read
from the environment and must be put in manually. :(

To run this app (on Linux):
$ python manage.py runserver -dr

To test on the command line (also on Linux):
$ python manage.py shell

When using on the command line, the app, db, User, Lit, and Role are already imported.

To test queries on Lit objects, you can use 'Book' and 'Biology Book' in the title field.
These are already stored in the DB.
