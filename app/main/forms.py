from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, FieldList, IntegerField, SelectField
from wtforms.validators import Required, Length, Email, Regexp, NumberRange
from wtforms import ValidationError
#from flask.ext.pagedown.fields import PageDownField
from ..models import User, Lit, Role
from wtforms.fields.html5 import EmailField

class NameForm(Form):
	name = StringField('What is your name?', validators = [Required()])
	submit = SubmitField('Submit')

class SearchForm(Form):
	search = StringField('Enter some terms to search on separated by a space:', validators = [Required()])
    	submit = SubmitField('Search')
    	
class ExactSearchForm(Form):
    	refType = SelectField('Reference Type', choices=[('None', None), ('journal', 'Journal'), ('article', 'Article'), ('magazine', 'Magazine'), ('textbook','Textbook'), ('book','Book')], default = None)
	title = StringField('Title', default = None)
	author = StringField('Author', default = None)
    	submit = SubmitField('Search')
    	
class AddLitForm(Form):
	refType = SelectField('Reference Type', validators = [Required()], choices=[('journal', 'Journal'), ('article', 'Article'), ('magazine', 'Magazine'), ('textbook','Textbook'), ('book','Book')])
    	title = StringField('Title', validators = [Required(), Length(1,150)])
    	author = StringField('Author', validators = [Required(), Length(1,120)])
    	description = TextAreaField('Description', validators = [Required(), Length(1,1000)])
    	#edition = IntegerField('Edition') 
    	#pages = StringField('Pages', validators = [Length(1,10)])
    	#yrPublished = IntegerField('Year Published', validators = [NumberRange(min=1800)]) # MUST ADD max_value!!! Limit it to THIS year!!
    	#tags = FieldList(StringField('Tags'))
    	#link = FieldList(StringField('Links'))
    	submit = SubmitField('Add')
    	
class DeleteUserForm(Form):
	email = EmailField("Email", validators=[Required()])
    	submit = SubmitField('Delete User')

class DeleteLitForm(Form):
	refType = SelectField('Reference Type', choices=[('None', None), ('journal', 'Journal'), ('article', 'Article'), ('magazine', 'Magazine'), ('textbook','Textbook'), ('book','Book')], default = None)
	title = StringField('Title', validators = [Required(), Length(1,150)])
    	author = StringField('Author', validators = [Required(), Length(1,120)])
    	submit = SubmitField('Delete Lit')

class EditProfileForm(Form):
 	name = StringField('Name', validators=[Length(0, 64)])
 	email = StringField('Email', validators=[Length(0, 64)])
 	location = StringField('Location', validators=[Length(0, 64)])
 	description = TextAreaField('About me')
 	submit = SubmitField('Submit')
    	
#class ConfirmDeleteUserForm(Form):
#	delete = BooleanField('Delete this user? It can\'t be taken back!', default = False, validators = [Required()])
#	submit = SubmitField('Delete User')
    	
