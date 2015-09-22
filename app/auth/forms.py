from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
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
 	name = StringField('Name', validators=[Required(), Length(1, 64)])
 	password = PasswordField('Password', validators=[Required(), EqualTo('password2', message='Passwords must match.')])
 	password2 = PasswordField('Confirm password', validators=[Required()])
 	reason = TextAreaField('Reason for wanting to join', validators=[Required()])
 	submit = SubmitField('Register')
 
 	def validate_email(self, field):
 		if User.objects(email__iexact=field.data).first():
 			raise ValidationError('Email already registered.')


class ReasonForm(Form):
	reason = StringField('Reasoning')
	submit = SubmitField('Submit')

class ChangePasswordForm(Form):
    old_password = PasswordField('Old password', validators=[Required()])
    password = PasswordField('New password', validators=[Required(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm new password', validators=[Required()])
    submit = SubmitField('Update Password')


class PasswordResetRequestForm(Form):
    email = StringField('Email', validators=[Required(), Length(3, 64), Email()])
    submit = SubmitField('Reset Password')


class PasswordResetForm(Form):
    email = StringField('Email', validators=[Required(), Length(3, 64), Email()])
    password = PasswordField('New Password', validators=[Required(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Reset Password')

    def validate_email(self, field):
        if User.objects(email__iexact = field.data).first() is None:
            raise ValidationError('Unknown email address.')


class ChangeEmailForm(Form):
    email = StringField('New Email', validators=[Required(), Length(3, 64), Email()])
    password = PasswordField('Password', validators=[Required()])
    submit = SubmitField('Update Email Address')

    def validate_email(self, field):
        if User.objects(email__iexact = field.data).first():
            raise ValidationError('Email already registered.')

