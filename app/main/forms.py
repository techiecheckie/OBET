from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, FieldList, IntegerField, SelectField
from wtforms.validators import Required, Length, Email, Regexp, NumberRange
from wtforms import ValidationError
#from flask.ext.pagedown.fields import PageDownField
from ..models import User, Lit, Role
from wtforms.fields.html5 import EmailField

class SearchForm(Form):
	search = StringField('Enter some terms to search on separated by a space:', validators = [Required()])
    	submit = SubmitField('Search')
    	
class ExactSearchForm(Form):
    	refType = SelectField('Reference Type', choices=[('Book Section','Book Section'), ('Edited Book', 'Edited Book') , ('Journal Article', 'Journal Article'), ('Journal Issue', 'Journal Issue'),
        ('Magazine Article', 'Magazine Article'), ('Media', 'Media'), ('Newspaper Article', 'Newspaper Article'), ('Report', 'Report'), ('Thesis', 'Thesis'), ('Website', 'Website')], default = None)
	title = StringField('Title', default = None)
	author = StringField('Author', default = None)
    	submit = SubmitField('Search')
    	
class AddLitForm(Form):
    refType = SelectField('Reference Type', validators = [Required()], choices=[('Book Section','Book Section'), ('Edited Book', 'Edited Book') , ('Journal Article', 'Journal Article'), ('Journal Issue', 'Journal Issue'),
        ('Magazine Article', 'Magazine Article'), ('Media', 'Media'), ('Newspaper Article', 'Newspaper Article'), ('Report', 'Report'), ('Thesis', 'Thesis'), ('Website', 'Website')])
    primaryField = SelectField('Primary Field', validators = [Required()], choices = [('Philosophy/Ethics/Theology','Philosophy/Ethics/Theology'), ('Anthropology/Psychology/Sociology','Anthropology/Psychology/Sociology'), ('History/Politics/Law','History/Politics/Law'), ('Agriculture/Energy/Industry','Agriculture/Energy/Industry'), ('Animal Science/Welfare','Animal Science/Welfare'), ('Ecology/Conservation','Ecology/Conservation'), ('Nature Writing/Art/Literary Criticism','Nature Writing/Art/Literary Criticism'), ('Education/Living','Education/Living')]) 
    secondaryField = SelectField('Secondary Field', choices = [('Philosophy/Ethics/Theology','Philosophy/Ethics/Theology'), ('Anthropology/Psychology/Sociology','Anthropology/Psychology/Sociology'), ('History/Politics/Law','History/Politics/Law'), ('Agriculture/Energy/Industry','Agriculture/Energy/Industry'), ('Animal Science/Welfare','Animal Science/Welfare'), ('Ecology/Conservation','Ecology/Conservation'), ('Nature Writing/Art/Literary Criticism','Nature Writing/Art/Literary Criticism'), ('Education/Living','Education/Living')])
    title = StringField('Title', validators = [Required(), Length(1,150)])
    author = StringField('Author', validators = [Length(1,120)])
    description = TextAreaField('Description', validators = [ Length(1,1000)])
	# edition = IntegerField('Edition') 
	# pages = StringField('Pages', validators = [Length(1,10)])
	# yrPublished = IntegerField('Year Published', validators = [NumberRange(min=1800)]) # MUST ADD max_value!!! Limit it to THIS year!!
	# tags = FieldList(StringField('Tags'))
	# link = FieldList(StringField('Links'))
    submit = SubmitField('Submit')   
    	
class DeleteUserForm(Form):
	email = EmailField("Email", validators=[Required()])
    	submit = SubmitField('Delete User')

class DeleteLitForm(Form):
	refType = SelectField('Reference Type', choices=[('Book Section','Book Section'), ('Edited Book', 'Edited Book') , ('Journal Article', 'Journal Article'), ('Journal Issue', 'Journal Issue'),
        ('Magazine Article', 'Magazine Article'), ('Media', 'Media'), ('Newspaper Article', 'Newspaper Article'), ('Report', 'Report'), ('Thesis', 'Thesis'), ('Website', 'Website')], default = None)
	title = StringField('Title', validators = [Required(), Length(1,150)])
        author = StringField('Author', validators = [Required(), Length(1,120)])
    	submit = SubmitField('Delete Lit')

class EditProfileForm(Form):
 	name = StringField('Name', validators=[Length(0, 64)])
 	credentials = StringField('Credentials', validators=[Length(0, 64)])
 	location = StringField('Location', validators=[Length(0, 64)])
 	description = TextAreaField('About me', validators=[Length(0, 1000)])
 	submit = SubmitField('Update Profile')
 	
    	
class EditProfileAdminForm(Form):
 	email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
 	role = SelectField('Role')
 	name = StringField('Real name', validators=[Length(1, 64)])
 	location = StringField('Location', validators=[Length(0, 64)])
 	description = TextAreaField('About me', validators=[Length(0, 1000)])
 	confirmed = BooleanField('Confirmed')
 	approved = BooleanField('Approved')
 	activated = BooleanField('Activated')
 	submit = SubmitField('Submit')

 	def __init__(self, user, *args, **kwargs):
 		super(EditProfileAdminForm, self).__init__(*args, **kwargs)
 		self.role.choices = [(role.name, role.name) for role in Role.objects()]
 		self.user = user
 
 	def validate_email(self, field):
 		if field.data != self.user.email and User.objects(email__iexact = field.data).first():
 			raise ValidationError('Email already registered.')
    	
