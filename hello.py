from flask import Flask, render_template, session, redirect, url_for, flash
from flask.ext.script import Manager
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment

from flask.ext.mongoengine import MongoEngine

from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required

##################
#    Config      #
##################
app = Flask(__name__)
app.config['SECRET_KEY'] = 'LSKFJDSLf84wi7rleIFdso8fsL9F87SDAOIFUSOH87FS70Q03958734LKdllkjdsflskjf'

###################
#    DB Config    #
###################

app.config['MONGO_URI'] = 'mongodb://mikachama:Haruka10@ds033419.mongolab.com:33419/inventory'
app.config['MONGODB_HOST'] = 'ds033419.mongolab.com'
app.config['MONGODB_PORT'] = 33419
app.config['MONGO_DBNAME'] = 'inventory'
app.config['MONGODB_USERNAME'] = 'mikachama'
app.config['MONGODB_PASSWORD'] = 'Haruka10'
app.config['ADMIN_EMAIL'] = 'admin@admin.com'
app.config['ADMIN_PASS'] = 'testerpassword'
app.config['MONGODB_SETTINGS'] = {
    'db': 'inventory',
    'host': 'mongodb://mikachama:Haruka10@ds033419.mongolab.com:33419/inventory'
}


###############
#    Init     #
###############

# Actually connects to the DB
def connect_db():
	connection = connect(app.config['MONGO_DBNAME'], username = app.config['MONGO_USERNAME'], password = app.config['MONGO_PASSWORD'], host = app.config['MONGO_URI'])
	print('Connected to DB.')
	return connection

def get_db():
	db = connect_db()
	db = db[app.config['MONGO_DBNAME']]

    	# Authenticate that connection
    	db.authenticate(app.config['MONGO_USERNAME'], app.config['MONGO_PASSWORD'])
    	return db


manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
db = MongoEngine(app)



##################
#    Errors      #
##################
@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
	return render_template('500.html'), 500


#################
#    Forms      #
#################
class NameForm(Form):
	name = StringField('What is your name?', validators = [Required()])
	submit = SubmitField('Submit')


##################
#    Routes      #
##################

@app.route('/index')
#def index():
#	return render_template('index.html')



@app.route('/', methods=['GET', 'POST'])
def index():
 form = NameForm()
 if form.validate_on_submit():
 	user = User.objects(name__iexact = form.name.data).first()
 	if user is None:
 		flash("You don't seem to be in the database!")
 		newUser = User(name=form.name.data, email=(form.data.name+'@OBET.com')).save()
 		flash("No worries, you've been added!")
 		session['known'] = False
 		if app.config['OBET_ADMIN']:
 			send_email(app.config['OBET_ADMIN'], 'New User', 'mail/new_user', user = user)
 	else:
 		flash(user.name + ' changed their name! Welcome back!')
 	session['known'] = True
 	session['name'] = form.name.data
 	form.name.data = ''
 	return redirect(url_for('index'))
 return render_template('index.html', form = form, name = session.get('name'))


"""@app.route('/', methods=['GET', 'POST'])
def index():
 	form = NameForm()
 	if form.validate_on_submit():
 		user = User.objects(name__iexact = form.name.data).first()
 		if user is None:
 			user = User(name = form.name.data, email = 'jollyanna@ct.com', hashPass = 'password')
 			flash('Trying to save your user here.')
 			#user.save()
 			#session['known'] = False
 			#if app.config['OBET_ADMIN']:
 			#	send_email(app.config['OBET_ADMIN'], 'New User', 'mail/new_user', user = user)
 		#else:
 			#session['known'] = True
 			#session['name'] = form.name.data
 		#form.name.data = ''
 		return redirect(url_for('index'))
 	return render_template('index.html', form = form, name = session.get('name'), known = session.get('known', False))"""

@app.route('/user/<name>')
def user(name):
	return render_template('user.html', name = name)


###################
#    Models    #
###################
from flask.ext.mongoengine.wtf import model_form
class User(db.Document):
    	name = db.StringField(max_length = 30, required = True)
    	credentials = db.StringField(max_length = 8)
    	email = db.EmailField(min_length = 3, max_length = 30) #, required = True, unique = True)
    	hashPass = db.StringField(max_length = 120) #, required = True)
    	site = db.URLField(max_length = 200, default = None)
    	description = db.StringField(max_length = 500) #, required = True)
    	#u_edit_record = ListField(EmbeddedDocumentField(UserEditRecord), default = [])

    	#def __repr__(self):
 	#	return '<User %r %r %r %r>' % self.name, self.email, self.hashPass


class Lit(db.Document):
    	refType = db.StringField(max_length = 30, required = True)
    	title = db.StringField(max_length = 120, required = True)
    	author = db.StringField(max_length = 30, required = True)
    	description = db.StringField(max_length = 500, required = True)
    	edition = db.IntField(min_value = 1, default = -1)
    	pages = db.IntField(min_value = 1, default = None)
    	yrPublished = db.IntField(min_value = 1800, default = None) # MUST ADD max_value!!! Limit it to THIS year!!
    	tags = db.ListField(StringField(max_length = 30), default = [])
    	link = db.URLField(max_length = 200, default = None)
    	#l_edit_record = ListField(EmbeddedDocumentField(LitEditRecord), default = [])

    	def __repr__(self):
 		return '<Lit %r>' % self.title

########################
#    Shell Context     #
########################

from flask.ext.script import Shell

def make_shell_context():
	return dict(app = app, db = db, User = User)

manager.add_command("shell", Shell(make_context = make_shell_context))


#####################
#    Mail Config    #
#####################
import os
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['OBET_MAIL_SUBJECT_PREFIX'] = '[OBET]'
app.config['OBET_MAIL_SENDER'] = 'OBET Admin <obet.correspondence@gmail.com>'
app.config['OBET_ADMIN'] = os.environ.get('OBET_ADMIN')

#####################################
#     Asynchronous Mail Support     #
#####################################

from flask.ext.mail import Message
from threading import Thread
from flask.ext.mail import Mail

mail = Mail(app)

def send_async_email(app, msg):
	with app.app_context():
		mail.send(msg)

def send_email(to, subject, template, **kwargs):
	msg = Message(app.config['OBET_MAIL_SUBJECT_PREFIX'] + subject,
	sender = app.config['OBET_MAIL_SENDER'], recipients = [to])
 	msg.body = render_template(template + '.txt', **kwargs)
 	msg.html = render_template(template + '.html', **kwargs)
 	thr = Thread(target = send_async_email, args = [app, msg])
	thr.start()
 	return thr




if __name__ == '__main__':
	manager.run()
