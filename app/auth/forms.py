#######################################################################
# Form definitions as classes for authentication related forms
#######################################################################

# Import the Form class, fields, and validators from wtform
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import Required, Email, Length, Regexp, EqualTo
from wtforms import ValidationError

# Import database models
from ..models import User, Role, Lit

# Each class is a subclass of Form from wtforms
# and defines the fields of the form and class attributes.
# StringField, PasswordField, etc. are imported from wtforms

# Login
class LoginForm(Form):
	email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
 	password = PasswordField('Password', validators=[Required()])
 	remember_me = BooleanField('Keep me logged in')
 	submit = SubmitField('Log In')

# Registration
class RegistrationForm(Form):
	email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
 	name = StringField('Name', validators=[Required(), Length(1, 64)])
 	password = PasswordField('Password', validators=[Required(), EqualTo('password2', message='Passwords must match.')])
 	password2 = PasswordField('Confirm password', validators=[Required()])
 	reason = TextAreaField('Reason for wanting to join', validators=[Required()])
 	submit = SubmitField('Register')
 
    # Check if the email provided exist in the database already
 	def validate_email(self, field):
 		if User.objects(email__iexact=field.data).first():
 			raise ValidationError('Email already registered.')

# Rejected user reason form
class ReasonForm(Form):
	reason = StringField('Reasoning')
	submit = SubmitField('Submit')

# User change password
class ChangePasswordForm(Form):
    old_password = PasswordField('Old password', validators=[Required()])
    password = PasswordField('New password', validators=[Required(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm new password', validators=[Required()])
    submit = SubmitField('Update Password')

# Request to reset password
class PasswordResetRequestForm(Form):
    email = StringField('Email', validators=[Required(), Length(3, 64), Email()])
    submit = SubmitField('Reset Password')

# Reset password
class PasswordResetForm(Form):
    email = StringField('Email', validators=[Required(), Length(3, 64), Email()])
    password = PasswordField('New Password', validators=[Required(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Reset Password')

    # Check if the email provided exists
    def validate_email(self, field):
        if User.objects(email__iexact = field.data).first() is None:
            raise ValidationError('Unknown email address.')

# Change email
class ChangeEmailForm(Form):
    email = StringField('New Email', validators=[Required(), Length(3, 64), Email()])
    password = PasswordField('Password', validators=[Required()])
    submit = SubmitField('Update Email Address')

    # Check if the email provided exist in the database already
    def validate_email(self, field):
        if User.objects(email__iexact = field.data).first():
            raise ValidationError('Email already registered.')

