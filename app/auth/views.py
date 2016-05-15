#####################################
# URL rules related to authentication
#####################################

# Import flask modules
from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user
from . import auth
# Import database models
from ..models import User, Role, Lit
# Import authentication forms defined in forms.py
from .forms import LoginForm, RegistrationForm, ReasonForm, ChangePasswordForm
from .forms import PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm

# login url
# ie. If user accesses "obet.herokuapp.com/login" this method is called
@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Create a new loginform
 	form = LoginForm()
    # If the request made to this url has a valid form submission
 	if form.validate_on_submit():
        # Search for the first email in the database that matches
 		user = User.objects(email__iexact = form.email.data).first()
        # If the user exists then verify their password
 		if user is not None and user.verify_password(form.password.data):
            # Set current user to be logged in
 			login_user(user, form.remember_me.data)
            # Redirect the user to the index page
 			return redirect(request.args.get('next') or url_for('main.index'))
        # Else display failed login message
 		flash('Invalid username or password.')
    # Return login page with form 
 	return render_template('auth/login.html', form = form)
 	

from flask.ext.login import logout_user, login_required
# logout url
@auth.route('/logout')
@login_required
def logout():
	logout_user()
 	flash('You have been logged out.')
    # Return main page
 	return redirect(url_for('main.index'))
 	
from ..email import send_email
from flask import current_app
from flask.ext.login import current_user
# Registration for users
@auth.route('/register', methods=['GET', 'POST'])
def register():
    # Create registration form
    form = RegistrationForm()
    # If the form is submitted and valid
    if form.validate_on_submit():
        # Create a new user
        user = User()
        # Set the attributes of the new user to form inputs
        user.email = form.email.data
        user.name = form.name.data
        user.password = form.password.data
        # Save the user to the database
        user.save()
        # Save form information as name, email, reason
        name = form.name.data
        email = form.email.data
        reason = form.reason.data
        # If the email matches the current admin's email then automatically approve
        if form.email.data == current_app.config['OBET_ADMIN']:
            flash('Welcome to OBET, new Admin! Please log in to continue.')
            user.approve()
            # Return login page
            return redirect(url_for('auth.login'))
        # Else, send an email to the admin, template found in "auth/email/adminConfirmation"
        send_email(current_app.config['OBET_ADMIN'], 'New User Information', 'auth/email/adminConfirmation', name = name, email = email, reason = reason)
        flash('The admin must approve your registration before you will be able to register. Check your email soon.')
 		#token = user.generate_confirmation_token()
 		#send_email(user.email, 'Confirm Your Account', 'auth/email/confirm', user=user, token=token)
 		#flash('A confirmation email has been sent to you by email.')
        # Redirect user to main page
        return redirect(url_for('main.index'))
    # If no form is submitted, return registration page
    return render_template('auth/register.html', form = form)



from ..decorators import admin_required
# Approve user, Admin approve user's application
@auth.route('/approveUser/<email>', methods=['GET', 'POST'])
@login_required
@admin_required
def approveUser(email):
    # Retrieve the the user (by email) from db
    user = User.objects(email__iexact = email).first()

    # If the user does not exist
    if user is None:
        # Redirect to main page with message
        flash('That user is no longer in the database to approve.')
        return redirect(url_for('main.index'))
        
    # If user is already confirmed, return to main page with message
    if user.confirmed:
        flash('This user has already been approved.')
        return redirect(url_for('main.index'))

    # Call generate_confirmation_token on User obj
    token = user.generate_confirmation_token() 	
    
    # Send email to user
    send_email(user.email, 'You\'ve been accepted to join OBET! Please confirm your account.', 'auth/email/confirm', user = user, token = token)
    flash('The user has been emailed their confirmation information.')
 	
    # Approve user
    user.approve()

    # return to main page
    return redirect(url_for('main.index'))


# Reject user, done by admin
@auth.route('/rejectUser/<email>', methods=['GET', 'POST'])
@login_required
@admin_required
def rejectUser(email):
    # Retrieve user from db
	user = User.objects(email__iexact = email).first()
	if user.confirmed:
			flash('This user has already been approved. Delete their account if you would like to remove them.')
 			return redirect(url_for('main.index'))
	if user is None:
		flash('That user is no longer in the database to approve.')
		return redirect(url_for('main.index'))
	form = ReasonForm()
    # If form submitted to reject usre
	if form.validate_on_submit():
		reason = form.reason.data
		admin = current_user
        # Send email to user on their rejection
 		send_email(user.email, 'Your OBET User Status', 'auth/email/rejectNotice', user = user, reason = reason, admin = admin)
 		flash('The user has been emailed their rejection.')
        # Delete user
 		user.delete()
        # Return admin to main page
 		return redirect(url_for('main.index'))
    # Else send "reject user" page
 	return render_template('auth/rejectUser.html', form = form)

# Activate user
@auth.route('/activate')
@login_required
def activate():
 	if current_user.activated:
 		flash('Already activated. Welcome back!')
 		return redirect(url_for('main.index'))
 	current_user.activate()
 	flash('Account reactivated! Welcome back!')
 	return render_template('main.index')

# Deactivate account
@auth.route('/deactivate')
@login_required
def deactivate():
 	if current_user.activated:
 		flash('Account already deactivated.')
 		return redirect(url_for('main.index'))
 	current_user.deactivate()
 	flash('Account deactivated! We\'ll miss you!')
 	return render_template('main.index')

# ??
@auth.route('/deactivated')
def deactivated():
 	if current_user.is_anonymous() or current_user.activated:
 		return redirect('main.index')
 	return render_template('auth/deactivated.html')

# Confirm email
from flask.ext.login import current_user
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
	if current_user.confirmed:
 		return redirect(url_for('main.index'))
    # Confirm user if not already
 	if current_user.confirm(token):
 		flash('You have confirmed your account. Thanks!')
 	else:
 		flash('The confirmation link is invalid or has expired.')
    # Send main page
 	return redirect(url_for('main.index'))

# Such a function is executed before each request, even if outside of a blueprint.
#   - flask docs
@auth.before_app_request
def before_request():
    # If user is not authenticated redirect them to "unconfirmed" page,
    # otherwise continue with their request
 	if current_user.is_authenticated() and not current_user.confirmed and request.endpoint[:5] != 'auth.':
 		#print "Before request function not working for some reason."
 		return redirect(url_for('auth.unconfirmed'))
 	#if current_user.is_authenticated() and not current_user.activated and request.endpoint[:5] != 'auth.':
 	#	return redirect(url_for('auth.deactivated'))

# Unconfirmed
@auth.route('/unconfirmed')
def unconfirmed():
 	if current_user.is_anonymous() or current_user.confirmed:
 		return redirect('main.index')
 	return render_template('auth/unconfirmed.html')


from ..email import send_email
# Resent confirmation
@auth.route('/confirm')
@login_required
def resend_confirmation():
 	token = current_user.generate_confirmation_token()
 	send_email(current_user.email, 'Confirm Your Account', 'auth/email/confirm', user = current_user, token=token)
 	flash('A new confirmation email has been sent to you by email.')
 	return redirect(url_for('main.index'))
 	
# Change password
@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    # Create new change password form
    form = ChangePasswordForm()
    # If the request contains a submitted form
    if form.validate_on_submit():
        # Verify the password is not the same as the old
        if current_user.verify_password(form.old_password.data):
            # Save new password
            current_user.password = form.password.data
            current_user.save()
            #db.session.add(current_user)
            flash('Your password has been updated.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password.')
    # Else, if there is no form submission send "change password" page
    return render_template("auth/change_password.html", form=form)

# Password reset request
@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    # If the user is logged in, do not allow them to reset password
    if not current_user.is_anonymous():
        return redirect(url_for('main.index'))
    # Else create new password reset request form
    form = PasswordResetRequestForm()
    # If a form is submitted
    if form.validate_on_submit():
        # Retrieve user from db
        user = User.objects(email__iexact = form.email.data).first()
        # If the user exists
        if user:
            # Generate reset token
            token = user.generate_reset_token()
            # Send email to user to reset password
            send_email(user.email, 'Reset Your Password',
                       'auth/email/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))
        flash('An email with instructions to reset your password has been '
              'sent to you.')
        # Return user to login
        return redirect(url_for('auth.login'))
    # Else if a form is not submitted give reset password page
    return render_template('auth/reset_password.html', form=form)

# Password reset
@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    # If the user is logged in, do not allow them to reset password
    if not current_user.is_anonymous():
        return redirect(url_for('main.index'))
    # Create new Password reset form
    form = PasswordResetForm()
    # If form is submitted
    if form.validate_on_submit():
        user = User.objects(email__iexact=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        # If successfully reset password
        if user.reset_password(token, form.password.data):
            flash('Your password has been updated.')
            # Redirect to login page
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)

# Change email request
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

# Change email
@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('Your email address has been updated.')
    else:
        flash('Invalid request.')
    return redirect(url_for('main.index'))

