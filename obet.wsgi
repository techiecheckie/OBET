activate_this = 'venv/bin/activate_this.py' #this is the path to the venv folder
execfile(activate_this, dict(__file__=activate_this))

from manage import app as application
