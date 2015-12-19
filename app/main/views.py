from datetime import datetime
from flask import render_template, session, redirect, url_for, flash
from . import main
from .forms import SearchForm, ExactSearchForm, AddLitForm, DeleteLitForm, DeleteUserForm, EditProfileForm
from .. import db
from ..models import User, Role, Lit, LitEditRecord, UserEditRecord
from flask.ext.login import login_required, current_user

#######################
# To be deleted later #
#######################
@main.route('/', methods=['GET', 'POST'])
def index():
 	return render_template('index.html', current_time = datetime.utcnow())


##################
# Fuzzy Search
##################

@main.route('/search', methods=['GET', 'POST'])
def search():
 form = SearchForm()
 if form.validate_on_submit():
 	print 'form is validated'
 	queryString = str(form.search.data)
 	lit = Lit.objects.search_text(queryString).order_by('$text_score')
 	if len(lit) == 0:
 			flash("Your search returned nothing. Try other search terms.")
 	else:
 		sortStr = str(form.sort.data)
 		# if sortStr == 'last_editdate' or sortStr == 'last_edituser':
 		# 	print 'trying to sort by embedded doc'
 		# 	lit = sorted(lit, key=lambda lit: getattr(getattr(lit, 'last_edit'), 'date'))
 		# 	# lit = sorted(lit, key=lambda lit: getattr(lit,'l_edit_record'))

 		# else:
 		lit = sorted(lit, key=lambda lit: getattr(lit, sortStr))
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


#####################
# User Profile Page #
#####################

@main.route('/user/<email>')
def user(email):
	user = User.objects(email__iexact = email).first()
	latest_activity = current_user.u_edit_record
	latest_activity = sorted(latest_activity, key=lambda la: la.date, reverse=True)
	latest_activity = latest_activity[0:5]
	return render_template('user.html', user = user, latest_activity = latest_activity)


#################
# Lit Main Page #
#################

@main.route('/lit/<lit_id>')
def lit(lit_id):
	lit = Lit.objects(id__iexact = lit_id).first()
	if lit is None:
		abort(404)
	return render_template('lit.html', lit = lit)


###########
# Add Lit #
###########

@main.route('/addLit', methods=['GET', 'POST'])
@login_required
def addLit():
	# isUpdate = False
 	form = AddLitForm()
 	if form.validate_on_submit():
		#########################################################
		# What should be here instead is an icontains statement showing the user similar entries
		# It should then allow the user to select if they would like to update or not,
		# and then update or add based on that
		#########################################################
		lit = Lit.objects(title__iexact = form.title.data, author__iexact = form.author.data).first()
		if lit is not None:
 			flash("This is already in the DB. This is the page")
 			## Change addLit to updateLit.
			return render_template('lit.html', lit = lit)
		
		editHist = LitEditRecord(lastUserEdited = current_user.name)

		lit = Lit(refType = form.refType.data, title = form.title.data, author = form.author.data, primaryField = form.primaryField.data, creator = current_user.name)
		lit.save()
		lit.update(set__yrPublished = form.yrPublished.data)
		lit.update(set__sourceTitle = form.sourceTitle.data)
		lit.update(set__editor = form.editor.data)
		lit.update(set__placePublished = form.placePublished.data)
		lit.update(set__publisher = form.publisher.data)
		lit.update(set__volume = form.volume.data)
		lit.update(set__number = form.number.data)
		lit.update(set__pages = form.pages.data)
		lit.update(set__abstract = form.abstract.data)
		lit.update(set__notes = form.notes.data)
		lit.update(set__secondaryField = form.secondaryField.data)

		if form.link.data is not None:
			print "this is the link: " + form.link.data
			lit.update(set__link = form.link.data)
		
		# Add keywords
		keywordslist = (form.keywords.data).split(",")
		print "this is the keywords: " + form.keywords.data
		for x in range(0, len(keywordslist)):
			key = str(keywordslist[x].strip())
			print key
			print type(key)
			lit.update(push__keywords = key)

		# Update lit history
		lit.update(push__l_edit_record=editHist)
		lit.update(set__last_edit = editHist)
		lit.reload()

		# Update user edit history
		userHist = UserEditRecord(litEdited = str(lit.id), operation = "add", litEditedTitle = lit.title)
		current_user.update(push__u_edit_record = userHist)
		current_user.reload()
		
		flash("Successfully added!")				
 		return redirect(url_for('main.lit', lit_id = lit.id))
 	return render_template('addLit.html', form = form)

##############
# Update Lit #
##############

@main.route('/updateLit/<lit_id>', methods=['GET','POST'])
@login_required
def updateLit(lit_id):
	lit = Lit.objects(id__iexact = lit_id).first()
	form = AddLitForm()
	keywordslist = ', '.join(lit.keywords).encode('utf-8')

	# Prepopulate the field with literature object information
	form.refType.data = lit.refType
	form.title.data = lit.title
	form.author.data = lit.author
	form.yrPublished.data = lit.yrPublished
	form.sourceTitle.data = lit.sourceTitle
	form.editor.data = lit.editor
	form.placePublished.data = lit.placePublished
	form.publisher.data = lit.publisher
	form.volume.data = lit.volume
	form.number.data = lit.number
	form.pages.data = lit.pages
	form.abstract.data = lit.abstract
	form.notes.data = lit.notes
	form.primaryField.data = lit.primaryField
	form.secondaryField.data = lit.secondaryField
	form.link.data = lit.link
	form.keywords.data = keywordslist
	return render_template('update.html', form = form, lit = lit)

#################
# submit Update #
#################

@main.route('/updateLitSub/<lit_id>', methods=['POST'])
@login_required
def updateLitSub(lit_id):
	form = AddLitForm()
	lit = Lit.objects(id__iexact = lit_id).first()
	if form.validate_on_submit():
		lit.update(set__title=form.title.data)
		lit.update(set__refType=form.refType.data)
		lit.update(set__author=form.author.data)
		lit.update(set__primaryField=form.primaryField.data)
		lit.update(set__yrPublished = form.yrPublished.data)
		lit.update(set__sourceTitle = form.sourceTitle.data)
		lit.update(set__editor = form.editor.data)
		lit.update(set__placePublished = form.placePublished.data)
		lit.update(set__publisher = form.publisher.data)
		lit.update(set__volume = form.volume.data)
		lit.update(set__number = form.number.data)
		lit.update(set__pages = form.pages.data)
		lit.update(set__abstract = form.abstract.data)
		lit.update(set__notes = form.notes.data)
		lit.update(set__secondaryField= form.secondaryField.data)
		lit.update(set__link = form.link.data)

		lit.update(set__keywords = [])
		keywordslist = (form.keywords.data).split(",")
		print "this is the keywords: " + form.keywords.data
		for x in range(0, len(keywordslist)-1):
			key = str(keywordslist[x].strip())
			if key is not None :
				lit.update(push__keywords = key)

		# Update Lit history	
		editHist = LitEditRecord(lastUserEdited = current_user.name)
		lit.update(push__l_edit_record=editHist)
		lit.update(set__last_edit = editHist)
		lit.reload()

		# Update User edit history
		userHist = UserEditRecord(litEdited = str(lit.id), operation = "update", litEditedTitle = lit.title)
		current_user.update(push__u_edit_record=userHist)
		current_user.reload()

		lit = Lit.objects(id__iexact = lit_id).first()
		flash(lit.title + " has been updated")
	else:
		flash(lit.title + " failed to be updated")
	return render_template('lit.html', lit = lit)

################
# Edit Profile #
################
## Need to add the update into this.
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
 	return render_template('editProfile.html', form=form)

#################################
# Delete Lit Main Page Function #
#################################

from ..decorators import admin_required, permission_required, user_required
@main.route('/deleteLit', methods=['GET', 'POST'])
@login_required
@admin_required
def deleteLit():
 	form = DeleteLitForm()
 	if form.validate_on_submit():
		queryString = str(form.search.data)
 		lit = Lit.objects.search_text(queryString).order_by('$text_score')
		if len(lit) == 0:
 			flash("Your search returned nothing. Try other search terms.")
 		else:
 			return render_template('deleteLit.html', form = form, lit = lit)
 		return redirect(url_for('main.deleteLit'))
 	return render_template('deleteLit.html', form = form)


##############################
# Delete Lit Helper Function #
##############################

@main.route('/lit/<lit_id>/delete', methods=['GET', 'POST'])
@login_required
@admin_required
def deleteLiterature(lit_id):
	lit = Lit.objects( id__exact = lit_id).first()
	if lit is None:
		flash("No literature like this in the database.")
	else:
		userHist = UserEditRecord(litEdited = str(lit_id), litEditedTitle = lit.title, operation = "delete")
		current_user.update(push__u_edit_record=userHist)
		current_user.reload()
		lit.delete()
		flash("Literature has been deleted!")				
	return redirect(url_for('main.search'))


###############
# Delete User #
###############
## Does not work the way we want, yet.

@main.route('/deleteUser', methods=['GET', 'POST'])
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
 	
 	
