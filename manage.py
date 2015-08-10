#!/usr/bin/env python
import os

if os.path.exists('.env'):
    print('Importing environment from .env...')
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]

from app import create_app, db
from app.models import User, Role, Lit
from flask.ext.script import Manager, Shell

app = create_app(os.getenv('OBET_CONFIG') or 'default')
manager = Manager(app)
#migrate = Migrate(app, db)

def make_shell_context():
	return dict(app = app, db = db, User = User, Role = Role, Lit = Lit)

manager.add_command("shell", Shell(make_context=make_shell_context))
#manager.add_command('db', MigrateCommand)

@manager.command
def test():
	#Run the unit tests.
 	import unittest
 	tests = unittest.TestLoader().discover('tests')
 	unittest.TextTestRunner(verbosity=2).run(tests)

if __name__ == '__main__':
	manager.run()
