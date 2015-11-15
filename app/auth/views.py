from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user
from . import auth
from ..models import User, Role, Lit
from .forms import LoginForm, RegistrationForm, ReasonForm, ChangePasswordForm
from .forms import PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm

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
from flask import current_app
from flask.ext.login import current_user
@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User()
        user.email = form.email.data
        user.name = form.name.data
        user.password = form.password.data
        user.save()
        name = form.name.data
        email = form.email.data
        reason = form.reason.data
        if form.email.data == current_app.config['OBET_ADMIN']:
            flash('Welcome to OBET, new Admin! Please log in to continue.')
            user.approve()
            return redirect(url_for('auth.login'))
        send_email('jaying.wu25@qmail.cuny.edu', 'New User Information', 'auth/email/adminConfirmation', name = name, email = email, reason = reason)
        flash('The admin must approve your registration before you will be able to register. Check your email soon.')
 		#token = user.generate_confirmation_token()
 		#send_email(user.email, 'Confirm Your Account', 'auth/email/confirm', user=user, token=token)
 		#flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form = form)



from ..decorators import admin_required

@auth.route('/approveUser/<email>', methods=['GET', 'POST'])
@login_required
@admin_required
def approveUser(email):
	user = User.objects(email__iexact = email).first()
	if user is None:
		flash('That user is no longer in the database to approve.')
		return redirect(url_for('main.index'))
	if user.confirmed:
		flash('This user has already been approved.')
 		return redirect(url_for('main.index'))
 	token = user.generate_confirmation_token() 	
 	send_email(user.email, 'You\'ve been accepted to join OBET! Please confirm your account.', 'auth/email/confirm', user = user, token = token)
 	flash('The user has been emailed their confirmation information.')
 	user.approve()
 	return redirect(url_for('main.index'))



@auth.route('/rejectUser/<email>', methods=['GET', 'POST'])
@login_required
@admin_required
def rejectUser(email):
	user = User.objects(email__iexact = email).first()
	if user.confirmed:
			flash('This user has already been approved. Delete their account if you would like to remove them.')
 			return redirect(url_for('main.index'))
	if user is None:
		flash('That user is no longer in the database to approve.')
		return redirect(url_for('main.index'))
	form = ReasonForm()
	if form.validate_on_submit():
		reason = form.reason.data
		admin = current_user
 		send_email(user.email, 'Your OBET User Status', 'auth/email/rejectNotice', user = user, reason = reason, admin = admin)
 		flash('The user has been emailed their rejection.')
 		user.delete()
 		return redirect(url_for('main.index'))
 	return render_template('auth/rejectUser.html', form = form)


@auth.route('/activate')
@login_required
def activate():
 	if current_user.activated:
 		flash('Already activated. Welcome back!')
 		return redirect(url_for('main.index'))
 	current_user.activate()
 	flash('Account reactivated! Welcome back!')
 	return render_template('main.index')



@auth.route('/deactivate')
@login_required
def deactivate():
 	if current_user.activated:
 		flash('Account already deactivated.')
 		return redirect(url_for('main.index'))
 	current_user.deactivate()
 	flash('Account deactivated! We\'ll miss you!')
 	return render_template('main.index')



@auth.route('/deactivated')
def deactivated():
 	if current_user.is_anonymous() or current_user.activated:
 		return redirect('main.index')
 	return render_template('auth/deactivated.html')


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


@auth.route('/unconfirmed')
def unconfirmed():
 	if current_user.is_anonymous() or current_user.confirmed:
 		return redirect('main.index')
 	return render_template('auth/unconfirmed.html')


from ..email import send_email
@auth.route('/confirm')
@login_required
def resend_confirmation():
 	token = current_user.generate_confirmation_token()
 	send_email(current_user.email, 'Confirm Your Account', 'auth/email/confirm', user = current_user, token=token)
 	flash('A new confirmation email has been sent to you by email.')
 	return redirect(url_for('main.index'))
 	

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            current_user.save()
            #db.session.add(current_user)
            flash('Your password has been updated.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password.')
    return render_template("auth/change_password.html", form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous():
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.objects(email__iexact = form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset Your Password',
                       'auth/email/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))
        flash('An email with instructions to reset your password has been '
              'sent to you.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous():
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.objects(email__iexact=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, 'Confirm your email address',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('An email with instructions to confirm your new email '
                  'address has been sent to you.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.')
    return render_template("auth/change_email.html", form=form)


@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('Your email address has been updated.')
    else:
        flash('Invalid request.')
    return redirect(url_for('main.index'))

