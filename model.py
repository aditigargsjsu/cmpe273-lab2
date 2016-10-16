from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from datetime import datetime



# Database Configurations
app = Flask(__name__)
DATABASE = 'crime_database'
PASSWORD = 'Password'
USER = 'root'
HOSTNAME = 'localhost'


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://%s:%s@%s/%s'%(USER, PASSWORD, HOSTNAME, DATABASE)
db = SQLAlchemy(app)

# Database migration command line


migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

class User(db.Model):

	# Data Model User Table
        id = db.Column(db.Integer, primary_key=True)
	street = db.Column(db.String(120), unique=False)
	type = db.Column(db.String(120), unique=False)
	time = db.Column(db.String(120),unique=False)	

	def __init__(self,street,type,time):
		# initialize columns
		self.street = street
		self.type = type
		self.time = time
		
	def __repr__(self):
		return '<User %r>' % self.name

# db.execute executes sql query like CREATE DATABASE IF NOT EXISTS etc.


class CreateDB():
	def __init__(self, hostname=None):
		if hostname != None:	
			HOSTNAME = hostname
		import sqlalchemy
		engine = sqlalchemy.create_engine('mysql://%s:%s@%s'%(USER, PASSWORD, HOSTNAME)) # connect to server
		engine.execute("DROP DATABASE IF EXISTS %s "%(DATABASE)) #delete db if an existing db is present. to get a new database for every time test is run.
		engine.execute("CREATE DATABASE IF NOT EXISTS %s "%(DATABASE)) #create db

if __name__ == '__main__':
	manager.run()
