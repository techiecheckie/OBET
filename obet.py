from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from pymongo import Connection
import pymongo
import sys
import os

app = Flask(__name__)

# configuration
app.config.update(dict(DEBUG = True,
SERVER = 'ds033419.mongolab.com',
PORT = 33419,
DATABASE = 'inventory',
SECRET_KEY = 'first site',
USERNAME = 'mikachama',
PASSWORD = 'Haruka10',
ADMIN_EMAIL = 'admin@admin.com',
ADMIN_PASS = 'testerpassword'
))


app.config.from_envvar('OBET_SETTINGS', silent=True)


@app.teardown_request
def teardown_request(exception):
	db = getattr(g, 'db', None)
	if db is not None:
	        db.close()
	        
@app.cli.command('initdb')
def initdb_command():
	init_db()
	print('DB initialized.')
	
def init_db():
	db = get_db()

def get_db():
	if not hasattr(g, 'db'):
		g.db = connect_db()
	return g.db
	
def connect_db():
	connection = Connection(app.config['SERVER'], app.config['PORT'])
	return connection
	# This used merely for testing connection to the DB
	"""print '\nGetting DB...'
	db = conn[app.config['DATABASE']]
	print '\nAuthenticating...'
	db.authenticate(app.config['USERNAME'], app.config['PASSWORD'])

	lit = db.literature
	print '\nNumber of lits', lit.find().count()

	results = lit.find()

	for record in results:
		print record
	"""

def dump_keys(d, lvl=0):
    for k, v in d.iteritems():
        print '%s%s' % (lvl * ' ', k)
        if type(v) == dict:
            dump_keys(v, lvl+1)

@app.route('/')
def mainPage():
    return render_template('index.html')
 
@app.route('/about')
def aboutPage():
	return render_template('about.html') 

@app.route('/search', methods = ['GET', 'POST'])
def fuzzySearch():
	error = None
    	# Configure the connection to the user collection in Mongo
    	db = get_db()
    	db = db[app.config['DATABASE']]
    	# Authenticate that connection
    	db.authenticate(app.config['USERNAME'], app.config['PASSWORD'])
    	# Selection the right collection
    	db = db['literature']
    	# Showing this until I know how record is configured
    	#f = request.form
    	#for key in f.keys():
    	#	for value in f.getlist(key):
        #		print key,":",value
        
        flash('Some searching will eventually go here after testing')
        results = db.find({'title': request.form['title'] }, 
		projection = {'tags': False}, 
		limit = 100)
	entries=[]
	for result in results:
		entries.append(dict(result))
	entries = [str(entries[0]["title"]), str(entries[0]["author"]), str(entries[0]["description"])]
	
    	#entries = [dict(title = 'The Land of the Lost', 
    	#	author = 'Aut McAuthor', 
    	#	description = 'Lorem ipsum etc etc')]
    	return render_template('index.html', entries = entries)

@app.route('/login', methods=['GET', 'POST'])
def login():
    	error = None
    	# Configure the connection to the user collection in Mongo
    	db = get_db()
    	db = db[app.config['DATABASE']]
    	# Authenticate that connection
    	db.authenticate(app.config['USERNAME'], app.config['PASSWORD'])
    	# Select the right collection
    	db = db['users']
    	# If this is a post request
    	if request.method == 'POST':
        	if request.form['email'].lower() != app.config['ADMIN_EMAIL']:
            		error = 'Email address not found. Only Professor Lahti has access at this time.'
        	elif request.form['password'] != app.config['ADMIN_PASS']:
            		error = 'Invalid password.'
        	else:
            		session['logged_in'] = True
            		flash('You were logged in. Welcome back, Professor Lahti!')
            		return redirect(url_for('admin_console'))
    	return render_template('login.html', error = error)
    	
    	
    	
    	# Something more similar to what the eventual code will look like
    	"""if request.method == 'POST':
    		# Grab email and password from the form
    		email = request.form['email']
    		password = request.form['password']
    		# If they're not in the database, write an error message
        	if db.find_one({'email': email, 'password': password}) is None:
            		error = 'Invalid username or password.'
        	# Otherwise log them in and set their session to logged in
        	# Then redirect to the admin_console.html template
        	else:
            		session['logged_in'] = True
            		flash('You were logged in')
            		return redirect(url_for('admin_console'))
        # Otherwise, show the error and leave them on the login page.    		
    	return render_template('login.html', error = error)
    	"""

@app.route('/addNew', methods=['GET', 'POST'])
def insertNewLiterature():
	# If you're not logged in, abort
    	if not session.get('logged_in'):
        	abort(401)
        # Configure the connection to the user collection in Mongo
    	db = get_db()
    	db = db[app.config['DATABASE']]
    	# Authenticate that connection
    	db.authenticate(app.config['USERNAME'], app.config['PASSWORD'])
    	db = db['literature']
    	# If a necessary field is missing, make them try again
	if (request.form['refType'] is None | request.form['title'] is None | request.form['author'] is None | request.form['description'] is None):
		return render_template('admin_console.html', error = "Error, entry must include the reference type, title, author, and description at least.")
	f = request.form
	# Print the values in the form so we can see how to insert in DB
	for key in f.keys():
    		for value in f.getlist(key):
        		print key,":",value
	
	# Will reinstate this later upon finding out the above		
	# db.insert_one()
    	flash('New literature successfully added.')
    	return redirect(url_for('insertNewLiterature'))
    	

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out. See you later, Professor Lahti!')
    return redirect(url_for('mainPage'))
    
if __name__ == "__main__":
    app.run(debug=True)

