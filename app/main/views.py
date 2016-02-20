from datetime import datetime
from flask import render_template, redirect, url_for, flash, request
from . import main
from .forms import SearchFormMain, SearchForm, AdvancedSearchForm, AddLitForm, DeleteLitForm, DeleteUserForm, EditProfileForm
from .. import db
from ..models import User, Role, Lit, LitEditRecord, UserEditRecord
from mongoengine.queryset.visitor import Q
from flask.ext.login import login_required, current_user
import json
import cgi

#######################
# To be deleted later #
#######################
@main.route('/', methods=['GET', 'POST'])
def index():
	form = SearchFormMain()
 	return render_template('index.html', form = form)


###############
# Information #
###############
@main.route('/about', methods=["GET"])
def about():
	return render_template('about.html')
	
@main.route('/history', methods=["GET"])
def history():
	return render_template('history.html')

@main.route('/manual', methods=['GET'])
def manual():
	return render_template('manAndInst.html')

##################
# Fuzzy Search
##################

def litToJson(lit):
	# Create a json string of lit
	jsonlit = '['
	for literature in iter(lit):
		jsonlit+= ( literature.to_json() + ", ")
	if len(jsonlit) > 7:
		jsonlit = jsonlit[:-2]
	jsonlit += "]"	
	return jsonlit

def convertId(lit):
	for l in lit:
		# Convert id to basic string id
		litid = "%s" % l["_id"]	
		litid = litid.replace("{u'$oid': u'", "")
		litid = litid.replace("'}", "")
		l["id"] = litid

		# Convert date to basic date
		litdate = "%s" % l["created_date"]
		litdate = litdate.replace("{u'$date': ", "")
		litdate = litdate.replace("L", "")
		litdate = int(litdate.replace("}", ""))
		litdate = litdate/1000.0
		litdate = str(datetime.fromtimestamp(litdate).strftime('%Y-%m-%d %H:%M:%S'))
		# print litdate
		l["created_date"] = litdate

		# Convert date to basic date
		if("last_edit" in l.keys()):
			litdate = "%s" % l["last_edit"]["date"]
			litdate = litdate.replace("{u'$date': ", "")
			litdate = litdate.replace("L", "")
			litdate = int(litdate.replace("}", ""))
			litdate = litdate/1000.0
			litdate = str(datetime.fromtimestamp(litdate).strftime('%Y-%m-%d %H:%M:%S'))
			# print "lastedit " + litdate
			l["last_edit"]["date"] = litdate

	return lit

def fuzzySearch(request):
 	form = SearchForm()
 	queryString = request['query']
 	form.search.data = queryString
 	if(queryString == ''):
 		flash("Your search returned nothing. Try other search terms.")
		return render_template('search.html', form = form, lit = None)

 	lit = Lit.objects.search_text(queryString).order_by('$text_score')
  	if len(lit) == 0:
 		flash("Your search returned nothing. Try other search terms.")
		return render_template('search.html', form = form, lit = lit)
	else:
		form.sort.data = ''

		# Convert lit to appropiate list object
		jsonlit = litToJson(lit)
		lit = json.loads(jsonlit)
		lit = convertId(lit)
		return render_template('search.html', form = form, lit = lit)

def refineView(request):
 	form = SearchForm()
 	
 	# Display all values in request for debugging purposed
 	f = request
	for key in f.keys():
		for value in f.getlist(key):
			print key,":",value

	# Set search term to original search term
	form.search.data = request['queryString']
	form.sort.data = request['sortStr']

	formString = request['redefinedString']
	if formString:
	 	lit = json.loads(formString)
	else:
	 	lit = none
	return render_template('search.html', form = form, lit = lit)

def searchForm(request):
 	form = SearchForm()
 	if request.search.data:
 		queryString = str(request.search.data)
 	lit = Lit.objects.search_text(queryString).order_by('$text_score')

 	if len(lit) == 0:
 		flash("Your search returned nothing. Try other search terms.")
		return render_template('search.html', form = form, lit = lit)

	else:
		# Sort lit
		if request.sort.data and str(request.sort.data) != 'None':
			sortStr = str(request.sort.data)
			lit = sorted(lit, key=lambda lit:getattr(lit, sortStr))

		# Convert lit to appropiate list object
		jsonlit = litToJson(lit)
		lit = json.loads(jsonlit)
		lit = convertId(lit)
		return render_template('search.html', form = form, lit = lit)

@main.route('/search', methods=['GET', 'POST'])
def search():
 form = SearchForm()	
 if request.method == 'POST':
	 # If the request is to search
	 if form.validate_on_submit():
	 	return searchForm(form)
	 # If the request is from the main page
	 elif request.form['submitBtn']=='main':
	 	return fuzzySearch(request.form)
 	 # If the request is to refine view
	 elif request.form['submitBtn']=='RefineView':
		return refineView(request.form)

 return render_template('search.html', form = form)

###################
# Advanced Search
###################

def convertCat(category):
	convertedString = ''
	# validate the string, excape all special chars
	# ...? 
	convertedString = cgi.escape(category, quote=True)

	return convertedString

def convertCont(contains):
	convertedString = ''
	# validate
	# ...
	convertedString = cgi.escape(contains, quote=True)

	return convertedString

def convertInp(inputtext):
	convertedString = ''
	
	convertedString = cgi.escape(inputtext, quote=True)
	print convertedString

	return convertedString

def convertCond(condition):
	convertedString = ''

	if(condition == "and"):
		return "&"
	elif(condition == "not"):
		return "ne"
	else:
		return "|"

def validInputText(inputtext):
	# ESCAPE SPECIAL CHRS
	inputtext = inputtext.strip()
	if(inputtext=="" or inputtext==None):
		return False
	else:
		return True

def createQuerySeg(x, first):
	querySeg = ""
	negation = ""

	# fields of each 
	category = 'category1'
	contains = 'contains1'
	inputtext = 'inputtext1'
	condition = 'condition1'

	categoryx = str.replace(category, '1', str(x))
	containsx = str.replace(contains, '1', str(x))
	inputtextx = str.replace(inputtext, '1', str(x))
	conditionx = str.replace(condition, '1', str(x))

	print categoryx
	print containsx
	print inputtextx
	print conditionx

	categorystring = request.form[categoryx]
	containsCond = request.form[containsx]
	inputtext = request.form[inputtextx]
	condition = request.form[conditionx]

	convertedCond = convertCond(condition)

	if(convertedCond=="ne"):
		negation = "__not"
		if(not first):
			querySeg += "&"
	elif(not first):
		querySeg += convertedCond

	if (validInputText(inputtext)):
		inputtext = convertInp(inputtext)
		containsCond = convertInp(containsCond)
		categorystring = convertCat(categorystring)

		# take the values and convert to model atribute names
		if(categorystring == 'KeywordsAbstractNotes'):
			querySeg += ('(Q(keywords' + negation + '__icontains ="' + inputtext + '") | Q(abstract' + 
				negation + '__icontains ="' + inputtext + '") | Q(notes' + negation + '__icontains ="' + inputtext + '"))')
		elif(categorystring == 'PrimarySecondary'):
			querySeg += ('(Q(primaryField' + negation + '__' + containsCond + ' ="' + inputtext + 
				'") | Q(secondaryField' + negation + '__' + containsCond + ' ="' + inputtext + '"))')
		elif(categorystring == 'CreatedBy'):
			querySeg += ('Q(creator' + negation + '__' + containsCond + ' ="' + inputtext + '")')
		elif(categorystring == 'ModifiedBy'):
			querySeg += ('Q(last_edit__lastUserEdited' + negation + '__' + containsCond + ' ="' + inputtext + '")')
		# else if for DATE
		elif(categorystring == 'DateCreated'):
			querySeg += ('Q()')
		else:
			querySeg += ("Q(" + categorystring + negation + "__" + 
			containsCond + " ='" + inputtext + "')")
	return querySeg

@main.route('/advancedSearch', methods=['GET', 'POST'])
def advancedSearch():
	if request.method == 'POST':
		cond = 'condition1'
		first = True
		print json.dumps(request.form)

		# get number of conditions
		count = int(request.form['count'])

		# string to contain the mongo query
		query = 'lit = Lit.objects('

		# go through all the conditions and add the information to 
		for x in xrange(1, count+1):

			condx = str.replace(cond, '1', str(x))
			print condx

			# check if the condition is ignore
			if( request.form[condx] != 'ignore' ):
				# print "This is the request " + request.form[condx] + " " + condx
				# if not ignore then add the information to the mongo query
				# get the information from the 4 input fields
				temp = createQuerySeg(x, first)
				if(temp != None and temp != ''):
					query += temp
					first = False

		query += (')')
		print query

		if( len(query) != 19 ):
			print 'LENGTH IS NOT 13'
			exec query
			# print json.dumps(lit)
			# lit = Lit.objects(Q(author__iexact = 'bob') | Q(keywords__icontains = 'only'))
			# print json.dumps(lit)

			if( len(lit)!=0):
				# Convert lit to appropiate list object
				jsonlit = litToJson(lit)
				lit = json.loads(jsonlit)
				lit = convertId(lit)
				sessioninfo = json.dumps(request.form)
				return render_template('AdvancedSearch.html', lit = lit, sessioninfo = sessioninfo)
			else:
				flash("Your query had no results.")

 	return render_template('AdvancedSearch.html')
		# execute the query

		# return the results as lit and the previous request as prevreq

 # form = AdvancedSearchForm()
 # if form.validate_on_submit():
 	
 # 	#####
 # 	# If there's nothing in the title or author areas, send an error and return.
 # 	if len(form.author.data) == 0 and len(form.title.data) == 0:
 # 		flash("You must enter something in the title or author sections.")
 # 		return redirect(url_for('main.advancedSearch'))
 	
 # 	#####
 # 	# If only title has data, grab info on that	
 # 	if len(form.author.data) == 0 and form.refType.data == 'None':
 # 		lit = Lit.objects(title__iexact = form.title.data)
 	
 # 	#####
 # 	# If only author has data, grab info on that	
 # 	elif len(form.title.data) == 0 and form.refType.data == 'None':
 # 		lit = Lit.objects(author__iexact = form.author.data)
 	
 # 	#####
 # 	# If both title and author have data, grab info on both
 # 	elif form.refType.data == 'None':
 # 		lit = Lit.objects(title__iexact = form.title.data, author__iexact = form.author.data)
 	
 # 	#####
 # 	# Otherwise grab everything
 # 	else:
 # 		lit = Lit.objects(title__iexact = form.title.data, author__iexact = form.author.data, refType__iexact = form.refType.data)
 	
 # 	#####
 # 	# If you don't find any matching objects, flash a message
 # 	if len(lit) == 0:
 # 			flash("Your search returned nothing. Try being less specific.")
 # 	# If you do, render them
 # 	else:
 # 		return render_template('advancedSearch.html', form = form, lit = lit)
 # 	# Either way, redirect back to this page
 # 	return redirect(url_for('main.advancedSearch'))
 # # If the form doesn't validate at all, rerender

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
	form = AddLitForm(None, lit)
	keywordslist = ', '.join(lit.keywords).encode('utf-8')

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
		for x in range(0, len(keywordslist)):
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
@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
 	form = EditProfileForm()
 	if form.validate_on_submit():
 		current_user.update(set__name=form.name.data)
 		current_user.update(set__location=form.location.data)
 		current_user.update(set__credentials = form.credentials.data)
 		current_user.update(set__description = form.description.data)
 		current_user.update(set__title = form.title.data)
 		current_user.update(set__author = form.author.data)
 		current_user.update(set__primaryField = form.primaryField.data)
 		current_user.update(set__editor = form.editor.data)
 		current_user.update(set__yearPublished = form.yearPublished.data)
 		current_user.update(set__refType = form.refType.data)
 		current_user.update(set__creator = form.creator.data)
 		current_user.update(set__dateCreatedOn = form.dateCreatedOn.data)
 		current_user.update(set__lastModified = form.lastModified.data)
 		current_user.update(set__lastModifiedBy = form.lastModifiedBy.data)
 		flash('Your profile has been updated.')
 		return redirect(url_for('.user', email = current_user.email))
 	form = EditProfileForm(None, current_user)
 	return render_template('editProfile.html', form=form)

#################################
# Delete Lit Main Page Function #
#################################
# Get rid of?

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
 	
 	
