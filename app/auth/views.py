from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user
from . import auth
from ..models import User, Role, Lit
from .forms import LoginForm, RegistrationForm

@auth.route('/login', methods=['GET', 'POST'])
def login():
 	form = LoginForm()
 	if form.validate_on_submit():
 		user = User.objects(email__iexact = form.email.data).first()
 		if user is not None and user.verify_password(form.password.data):
 			login_user(user, form.remember_me.data)
 			return redirect(request.args.get('next') or url_for('main.index'))
 		flash('Invalid username or password.')
 	return render_template('auth/login.html', form = form)
 	

from flask.ext.login import logout_user, login_required

@auth.route('/logout')
@login_required
def logout():
	logout_user()
 	flash('You have been logged out.')
 	return redirect(url_for('main.index'))
 	
from ..email import send_email
 	
@auth.route('/register', methods=['GET', 'POST'])
def register():
 	form = RegistrationForm()
 	if form.validate_on_submit():
 		user = User()
 		user.email = form.email.data
 		user.name = form.name.data
 		user.password = form.password.data
 		user.save()
 		token = user.generate_confirmation_token()
 		send_email(user.email, 'Confirm Your Account', 'auth/email/confirm', user=user, token=token)
 		flash('A confirmation email has been sent to you by email.')
 		return redirect(url_for('main.index'))
 	return render_template('auth/register.html', form = form)


from flask.ext.login import current_user
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
	if current_user.confirmed:
 		return redirect(url_for('main.index'))
 	if current_user.confirm(token):
 		flash('You have confirmed your account. Thanks!')
 	else:
 		flash('The confirmation link is invalid or has expired.')
 	return redirect(url_for('main.index'))


@auth.before_app_request
def before_request():
 	if current_user.is_authenticated() and not current_user.confirmed and request.endpoint[:5] != 'auth.':
 		#print "Before request function not working for some reason."
 		return redirect(url_for('auth.unconfirmed'))
 	#if current_user.is_authenticated() and not current_user.activated and request.endpoint[:5] != 'auth.':
 	#	return redirect(url_for('auth.deactivated'))
 	
#@auth.before_app_request
#def before_request():
# 	if current_user.is_authenticated():
# 		current_user.ping()
# 		if not current_user.confirmed and request.endpoint[:5] != 'auth.':
# 			return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
 	if current_user.is_anonymous() or current_user.confirmed:
 		return redirect('main.index')
 	return render_template('auth/unconfirmed.html')

## Cannot test activation until users in the DB are updated
#@auth.route('/deactivated')
#def deactivated():
# 	if not current_user.activated:
# 		return redirect('main.index')
# 	return render_template('auth/deactivated.html')

from ..email import send_email
@auth.route('/confirm')
@login_required
def resend_confirmation():
 	token = current_user.generate_confirmation_token()
 	send_email('auth/email/confirm', 'Confirm Your Account', user = current_user, token=token)
 	flash('A new confirmation email has been sent to you by email.')
 	return redirect(url_for('main.index'))

