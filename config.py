import os
basedir = os.path.abspath(os.path.dirname(__file__))
class Config:
	SECRET_KEY = 'LSKFJDSLf84wi7rleIFdso8fsL9F87SDAOIFUSOH87FS70Q03958734LKdllkjdsflskjf'
	MAIL_SERVER = 'smtp.gmail.com'
 	MAIL_PORT= 587
	MAIL_USE_TLS = True
 	OBET_MAIL_SUBJECT_PREFIX = '[OBET]'
 	OBET_MAIL_SENDER = 'OBET Admin <obet.correspondence@gmail.com>'
	OBET_ADMIN = 'oddlypaired@gmail.com' #os.environ.get('OBET_ADMIN')
	MAIL_USERNAME = 'obet.correspondence@gmail.com' #os.environ.get('MAIL_USERNAME')
 	MAIL_PASSWORD = 'OBETCorr' #os.environ.get('MAIL_PASSWORD')

	@staticmethod
	def init_app(app):
		pass

class DevelopmentConfig(Config):
	DEBUG = True
 	MONGO_URI = 'mongodb://mikachama:Haruka10@ds033419.mongolab.com:33419/inventory'
	MONGO_DBNAME = 'inventory'
	MONGODB_USERNAME = 'mikachama'
	MONGODB_PASSWORD = 'Haruka10'
	MONGODB_SETTINGS = {
		'db': 'inventory',
    		'host': 'mongodb://mikachama:Haruka10@ds033419.mongolab.com:33419/inventory'
	}

class TestingConfig(Config):
	TESTING = True
 	MONGO_URI = 'mongodb://mikachama:Haruka10@ds033419.mongolab.com:33419/inventory'
	MONGO_DBNAME = 'inventory'
	MONGODB_USERNAME = 'mikachama'
	MONGODB_PASSWORD = 'Haruka10'
	MONGODB_SETTINGS = {
		'db': 'inventory',
    		'host': 'mongodb://mikachama:Haruka10@ds033419.mongolab.com:33419/inventory'
	}

class ProductionConfig(Config):
 	MONGO_URI = 'mongodb://mikachama:Haruka10@ds033419.mongolab.com:33419/inventory'
	MONGO_DBNAME = 'inventory'
	MONGODB_USERNAME = 'mikachama'
	MONGODB_PASSWORD = 'Haruka10'
	MONGODB_SETTINGS = {
		'db': 'inventory',
    		'host': 'mongodb://mikachama:Haruka10@ds033419.mongolab.com:33419/inventory'
	}
	
config = {
	'development': DevelopmentConfig,
	'testing': TestingConfig,
 	'production': ProductionConfig,
 	'default': DevelopmentConfig
}
