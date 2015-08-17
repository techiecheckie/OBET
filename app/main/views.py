from datetime import datetime
from flask import render_template, session, redirect, url_for, flash
from . import main
from .forms import NameForm, SearchForm, ExactSearchForm, AddLitForm, DeleteLitForm, DeleteUserForm
from .. import db
from ..models import User, Role, Lit
from flask.ext.login import login_required, current_user

#######################
# To be deleted later #
#######################
@main.route('/', methods=['GET', 'POST'])
def index():
 form = NameForm()
 if form.validate_on_submit():
 	user = User.objects(name__iexact = form.name.data).first()
 	if user is None:
 		flash("You don't seem to be in the database!")
 		newUser = User(name = form.name.data, email=(form.name.data+'@OBET.com'), hashPass = (form.name.data+'Password')).save()
 		flash("No worries, you've been added!")
 		session['known'] = False
 		if app.config['OBET_ADMIN']:
 			send_email(app.config['OBET_ADMIN'], 'New User', 'mail/new_user', user = user)
 	else:
 		flash('Welcome back, ' + user.name + '! Great to see you again! ')
 	session['known'] = True
 	session['name'] = form.name.data
 	form.name.data = ''
 	return redirect(url_for('index'))
 return render_template('index.html', form = form, name = session.get('name'), known=session.get('known', False), current_time=datetime.utcnow())


#########################
# Fuzzy Search
##################

@main.route('/search', methods=['GET', 'POST'])
def search():
 form = SearchForm()
 if form.validate_on_submit():
 	queryString = str(form.search.data)
 	lit = Lit.objects.search_text(queryString).order_by('$text_score')
 	if len(lit) == 0:
 			flash("Your search returned nothing. Try other search terms.")
 	else:
 		return render_template('search.html', form = form, lit = lit)
 	return redirect(url_for('main.search'))
 return render_template('search.html', form = form)

###############
# Strict Search
###################

@main.route('/exactSearch', methods=['GET', 'POST'])
def exactSearch():
 form = ExactSearchForm()
 if form.validate_on_submit():
 	
 	#####
 	# If there's nothing in the title or author areas, send an error and return.
 	if len(form.author.data) == 0 and len(form.title.data) == 0:
 		flash("You must enter something in the title or author sections.")
 		return redirect(url_for('main.exactSearch'))
 	
 	#####
 	# If only title has data, grab info on that	
 	if len(form.author.data) == 0 and form.refType.data == 'None':
 		lit = Lit.objects(title__iexact = form.title.data)
 	
 	#####
 	# If only author has data, grab info on that	
 	elif len(form.title.data) == 0 and form.refType.data == 'None':
 		lit = Lit.objects(author__iexact = form.author.data)
 	
 	#####
 	# If both title and author have data, grab info on both
 	elif form.refType.data == 'None':
 		lit = Lit.objects(title__iexact = form.title.data, author__iexact = form.author.data)
 	
 	#####
 	# Otherwise grab everything
 	else:
 		lit = Lit.objects(title__iexact = form.title.data, author__iexact = form.author.data, refType__iexact = form.refType.data)
 	
 	#####
 	# If you don't find any matching objects, flash a message
 	if len(lit) == 0:
 			flash("Your search returned nothing. Try being less specific.")
 	# If you do, render them
 	else:
 		return render_template('exactSearch.html', form = form, lit = lit)
 	# Either way, redirect back to this page
 	return redirect(url_for('main.exactSearch'))
 # If the form doesn't validate at all, rerender
 return render_template('exactSearch.html', form = form)


#@main.route('/lit/<title>')
#def lit(title):
#	lit = Lit.objects(title__iexact = title).first()
#	if lit is None:
#		abort(404)
#	 return render_template('lit.html', lit = lit)

@main.route('/user/<email>')
def user(email):
	user = User.objects(email__iexact = email).first()
	if user is None:
		abort(404)
	return render_template('user.html', user = user)



@main.route('/addLit')
@login_required
def addLit():
	isUpdate = False
 	form = AddLitForm()
 	if form.validate_on_submit():
		#########################################################
		# What should be here instead is an icontains statement showing the user similar entries
		# It should then allow the user to select if they would like to update or not,
		# and then update or add based on that
		#########################################################
		lit = Lit.objects(title__iexact = form.title.data, author__iexact = form.author.data).first()
		if len(lit) != 0:
 			flash("This is already in the DB. Updating instead.")
			isUpdate = True
		lit = Lit(refType = form.refType.data, title = form.title.data, author = form.author.data, description=form.description.data)
		flash("Problem is not with creating object but with saving object.")
		lit.save()
		if isUpdate:
			flash("Updated the entry.")
		else:
			flash("Added new entry to the DB.")				
 		return redirect(url_for('main.addLit'))
 	return render_template('addLit.html', form = form)
 

@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
 	form = EditProfileForm()
 	if form.validate_on_submit():
 		current_user.name = form.name.data
 		current_user.credentials = form.credentials.data
 		current_user.description = form.description.data
 		flash('Your profile has been updated.')
 		return redirect(url_for('.user', email = current_user.email))
 	form.name.data = current_user.name
 	form.credentials.data = current_user.credentials
 	form.description.data = current_user.description
 	return render_template('edit_profile.html', form=form)

#@main.route('/<name>/deactivateAcct')
#@login_required
#@user_required
#deactivate
#def deactivateAcct:
#	form = DeactivateForm()
# 	if form.validate_on_submit():
#			current_user.activated = False			
# 		return redirect(url_for('main.addLit'))
# 	return render_template('addLit.html', name = current_user.name, form = form)
#changeEmail
#changePass

from ..decorators import admin_required, permission_required, user_required
@main.route('/deleteLit')
@login_required
@admin_required
def deleteLit():
 	form = DeleteLitForm()
 	if form.validate_on_submit():
		#########################################################
		# What should be here instead is an icontains statement showing the user similar entries
		# It should then allow the user to select if they would like to delete or not,
		# and then delete based on that
		#########################################################
		lit = Lit.objects(title__iexact = form.title.data, author__iexact = form.author.data).first()
		if lit is None:
 			flash("No literature like this in the database.")
 		else:
 			lit.delete()
 			flash(form.title.data + " literature has been deleted!")				
 		return redirect(url_for('main.deleteLit'))
 	return render_template('deleteLit.html', form = form)

@main.route('/deleteUser')
@login_required
@admin_required
def deleteUser():
 	form = DeleteUserForm()
 	if form.validate_on_submit():
		user = User.objects(email__iexact = form.email.data).first()
		if user is None:
 			flash("No user like this in the database.")
 		else:
 			user.delete()
 			flash("User Deleted.")
 		return redirect(url_for('main.deleteUser'))
 	return render_template('deleteUser.html', form = form)
 	
 	

 	
#@main.route('/<name>/deleteUser/<userEmail>')
#@login_required
#@admin_required
#def confirmDeleteUser():
#	form = ConfirmDeleteUserForm()
#	if form.validate_on_submit():
#		user.delete()
 #		flash("User deleted.")				
 #		return redirect(url_for('main.deleteUser'))
 #	return render_template('deleteUser.html', name = current_user.name, form = form)
