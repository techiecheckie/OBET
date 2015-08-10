from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Email, Length
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User, Role, Lit

class LoginForm(Form):
	email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
 	password = PasswordField('Password', validators=[Required()])
 	remember_me = BooleanField('Keep me logged in')
 	submit = SubmitField('Log In')
 	


class RegistrationForm(Form):
	email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
 	name = StringField('Name', validators=[Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Names must have only letters, numbers, dots or underscores')])
 	password = PasswordField('Password', validators=[Required(), EqualTo('password2', message='Passwords must match.')])
 	password2 = PasswordField('Confirm password', validators=[Required()])
 	submit = SubmitField('Register')
 
 	def validate_email(self, field):
 		if User.objects(email__iexact=field.data).first():
 			raise ValidationError('Email already registered.')
