from flask import Flask, render_template
from flask.ext.bootstrap import Bootstrap
from flask.ext.mail import Mail
from flask.ext.moment import Moment
from flask.ext.mongoengine import MongoEngine
from config import config
from flask.ext.login import LoginManager

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = MongoEngine()

def create_app(config_name):
 	app = Flask(__name__)
 	app.config.from_object(config[config_name])
 	config[config_name].init_app(app)
 	bootstrap.init_app(app)
 	mail.init_app(app)
 	moment.init_app(app)
 	db.init_app(app)
 	login_manager.init_app(app)
 	
 	from main import main as main_blueprint
 	app.register_blueprint(main_blueprint)
 	
 	from .auth import auth as auth_blueprint
 	app.register_blueprint(auth_blueprint, url_prefix='/auth')
 # attach routes and custom error pages here
 	return app
 

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
