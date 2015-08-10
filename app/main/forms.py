from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, FieldList, IntegerField, SelectField
from wtforms.validators import Required, Length, Email, Regexp, NumberRange
from wtforms import ValidationError
#from flask.ext.pagedown.fields import PageDownField
from ..models import User, Lit, Role

class NameForm(Form):
	name = StringField('What is your name?', validators = [Required()])
	submit = SubmitField('Submit')

class SearchForm(Form):
	refType = SelectField('Reference Type', choices=[('jo', 'Journal'), ('ar', 'Article'), ('ma', 'Magazine'), ('tx','Textbook'), ('bo','Book')])
	title = StringField('Title', validators = [Required()])
	author = StringField('Author')
    	#edition = IntegerField('Edition')
    	tags = FieldList(StringField('Tags'))
    	submit = SubmitField('Search')
    	
    	
class AddLitForm(Form):
	refType = SelectField('Reference Type', validators = [Required()], choices=[('jo', 'Journal'), ('ar', 'Article'), ('ma', 'Magazine'), ('tx','Textbook'), ('bo','Book')])
    	title = StringField('Title', validators = [Required(), Length(1,120)])
    	author = StringField('Author', validators = [Required(), Length(1,120)])
    	description = TextAreaField('Description', validators = [Required(), Length(1,500)])
    	edition = IntegerField('Edition') 
    	pages = StringField('Pages', validators = [Length(1,10)])
    	yrPublished = IntegerField('Year Published', validators = [NumberRange(min=1800)]) # MUST ADD max_value!!! Limit it to THIS year!!
    	tags = FieldList(StringField('Tags'))
    	link = FieldList(StringField('Links'))
    	submit = SubmitField('Add')
    	
