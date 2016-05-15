# coding=utf-8

############################
# URL rules
############################

from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, make_response
from . import main
from .forms import SearchFormMain, SearchForm, AdvancedSearchForm, AddLitForm, DeleteLitForm, DeleteUserForm, EditProfileForm, Preferences
from .. import db
# Import database model
from ..models import User, Role, Lit, LitEditRecord, UserEditRecord
from mongoengine.queryset.visitor import Q
from flask.ext.login import login_required, current_user
import json, cgi, csv, io, collections

#######################
# Main Page #
#######################

@main.route('/', methods=['GET', 'POST'])
def index():

	# Create new main page search form
	form = SearchFormMain()

	# Get the number of objects in the "lit" collection of the db
	litcount = Lit.objects.count()

	# Render and return main page (index.html)
 	return render_template('index.html', form = form, litcount = litcount)

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

##########
# Browse #
##########

@main.route('/browse', methods=['GET'])
def browse():

	# Retrieve the first 50 lit objects from the db
	lit = Lit.objects[:50].order_by('-created_date')

	# Get 'preferences' cookie
	preferences = request.cookies.get('preferences')

	# If the cookie doesnt exist 
	if not preferences: 

		# Return default preferences
		preferences = default_pref

	else: 

		# Otherwise convert the cookie to a python object
		preferences = json.loads(preferences)

	# Render template with the list of literature and preferences obj and send to client
	return render_template('browse.html', lit=lit, preferences=preferences)

##################
# Fuzzy Search
##################

# Utility function
def litToJson(lit):

	# Create a json string of lit
	jsonlit = '['
	for literature in iter(lit):
		jsonlit+= ( literature.to_json() + ", ")

	# Remove the last comma and space
	if len(jsonlit) > 7:
		jsonlit = jsonlit[:-2]
	jsonlit += "]"	
	return jsonlit

# Utility function to convert lit object into string
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
		l["created_date"] = litdate

		# Convert date to basic date
		if("last_edit" in l.keys()):
			litdate = "%s" % l["last_edit"]["date"]
			litdate = litdate.replace("{u'$date': ", "")
			litdate = litdate.replace("L", "")
			litdate = int(litdate.replace("}", ""))
			litdate = litdate/1000.0
			litdate = str(datetime.fromtimestamp(litdate).strftime('%Y-%m-%d %H:%M:%S'))
			l["last_edit"]["date"] = litdate

	return lit

# Utility function to
# append creator name to the literature object being returned to the template
def appendCreatorName(lit):
	for l in lit:
		l["creator_name"] = lit

# Request coming from the main page
# Return the template for regular search 
def fuzzySearch(request):

	# Create new search form
 	form = SearchForm()

 	# Save information in request
 	req_form = request.form

 	# Save query made to return with the page so users can see the query they made previously
 	queryString = req_form['query']

 	# Set the search string in the new form to the old query
 	form.search.data = queryString

 	# If the user searched with an empty string simply return
 	if(queryString == ''):
 		flash("Your search returned nothing. Try other search terms.")
		return render_template('search.html', form = form, lit = None)

	# Otherwise so a text search in the database
 	lit = Lit.objects.search_text(queryString).order_by('$text_score')

  	# If there were no results, return page
  	if len(lit) == 0:
 		flash("Your search returned nothing. Try other search terms.")
		return render_template('search.html', form = form, lit = lit)

	# Otherwise return the page with the search results
	else:
		form.sort.data = ''

		# Convert lit to appropiate list object
		jsonlit = litToJson(lit)
		lit = json.loads(jsonlit)
		lit = convertId(lit)

		# Get 'preferences' cookie
		preferences = request.cookies.get('preferences')

		# If the cookie doesnt exist 
		if not preferences: 

			# Return default preferences
			preferences = default_pref

		else:

			# Otherwise convert the cookie to a python object
			preferences = json.loads(preferences)
		return render_template('search.html', form = form, lit = lit, preferences = preferences)

# Regular search
def searchForm(request, req_form):
 	form = SearchForm()
 	if req_form.search.data:
 		queryString = str(req_form.search.data)

 	lit = Lit.objects.search_text(queryString).order_by('$text_score')

 	if len(lit) == 0:
 		flash("Your search returned nothing. Try other search terms.")
		return render_template('search.html', form = form, lit = lit)

	else:
		# Sort lit
		if req_form.sort.data and str(req_form.sort.data) != 'None':
			sortStr = str(req_form.sort.data)
			lit = sorted(lit, key=lambda lit:getattr(lit, sortStr))

		# Convert lit to appropiate list object
		jsonlit = litToJson(lit)
		lit = json.loads(jsonlit)
		lit = convertId(lit)

		# Get 'preferences' cookie
		preferences = request.cookies.get('preferences')

		# If the cookie doesnt exist 
		if not preferences: 

			# Return default preferences
			preferences = default_pref

		else: 

			# Otherwise convert the cookie to a python object
			preferences = json.loads(preferences)
		return render_template('search.html', form = form, lit = lit, preferences = preferences)

# Handles request for search page
@main.route('/search', methods=['GET', 'POST'])
def search():
 form = SearchForm()	
 if request.method == 'POST':

	 # If the request is to search
	 if form.validate_on_submit():
	 	return searchForm(request, form)

	 # If the request is from the main page
	 elif request.form['submitBtn']=='main':
	 	return fuzzySearch(request)
	 elif request.form['submitBtn']=='Export':
	 	return downloadResults(request.form)

 	 # If the request is to refine the list of search results
	 elif request.form['submitBtn']=='RefineList':
		return refineList(request, "reg")

 # Otherwise return regular search page
 return render_template('search.html', form = form)

########################
# Export to CSV
########################

# Utility function to delete specified keys 
#  *keys is any number of arguments after it
# it is the dict item
def dict_filter(it, *keys):
    for item in it:
	    for k in keys:
	    	del item[k]

# Recursively encode items in dict to utf-8 	
def encode(data):
    if isinstance(data, basestring):
        return data.encode('utf8', 'ignore')
    elif isinstance(data, collections.Mapping):
        return dict(map(encode, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(encode, data))
    else:
        return data

# This route will prompt a file download with the csv lines
def downloadResults(request_form):

	# Get search results they want to export
	formString = request_form['redefinedString']

	# Convert to python object
	search_results = json.loads(formString)

	# Get list of id's from the redefined string
	id_list = []
	for item in search_results:
		id_list.append(item["id"])

	# Query the database for those lit
	lit = Lit.objects(id__in=id_list)

	# Create a json from that result
	lit = litToJson(lit)
	lit = json.loads(lit)

	# Remove unnecessary fields
	header = sorted(["abstract","author","editor","keywords","link","notes","number","pages","placePublished","primaryField","publisher","refType","secondaryField","sourceTitle","title","volume","yrPublished"])
	dict_filter(lit, "_id", "l_edit_record", "last_edit", "created_date", "creator")
	header = encode(header)

	# Transfrom it into a tsv with DictWriter
	sio = io.BytesIO()
	dw = csv.DictWriter(sio, header, delimiter='\t')
	dw.writeheader()
	for l in lit:
		l = encode(l)
		print str(l)
		dw.writerow(l)

    # We need to modify the response, so the first thing we 
    # need to do is create a response out of the CSV string
	response = make_response(sio.getvalue())

    # This is the key: Set the right header for the response
    # to be downloaded, instead of just printed on the browser
	response.headers["Content-Disposition"] = "attachment; filename=obet_search.tsv"
	return response

###################
# Refine List 
###################
# Refine the list of search results to those user specifies
def refineList(request, search):

	# If refine list comes from the advanced search 
	if(search == "adv"):

		# Take the data from the request
		req_form = request.form
		
		# Save the query
		formString = req_form['redefinedString']
		
		# Load the string into a python dict if it exists
		if formString:
		 	lit = json.loads(formString)
		else:
		 	lit = none

		# Get 'preferences' cookie
		preferences = request.cookies.get('preferences')

		# If the cookie doesnt exist 
		if not preferences: 

			# Return default preferences
			preferences = default_pref
		else: 

			# Otherwise convert the cookie to a python object
			preferences = json.loads(preferences)
 		return render_template('AdvancedSearch.html', lit = lit, sessioninfo = req_form['queryString'], preferences = preferences)
 	
 	# Otherwise the request is from a the regular search
 	else:

 		# Save request data
 		req_form = request.form

 		# Create new search form
	 	form = SearchForm()
	 	
	 	# Display all values in request for debugging 

	 # 	f = request
		# for key in f.keys():
		# 	for value in f.getlist(key):
		# 		print key,":",value

		# Set search term in form to original search term
		form.search.data = req_form['queryString']
		form.sort.data = req_form['sortStr']

		# Save refined json string array of lit
		formString = req_form['redefinedString']

		# Convert the json array into python list
		if formString:
		 	lit = json.loads(formString)
		else:
		 	lit = none

		# Get 'preferences' cookie
		preferences = request.cookies.get('preferences')

		# If the cookie doesnt exist 
		if not preferences: 

			# Return default preferences
			preferences = default_pref

		else:

			# Otherwise convert the cookie to a python object
			preferences = json.loads(preferences)
		return render_template('search.html', form = form, lit = lit, preferences = preferences)

###################
# Advanced Search
###################

# Utility functions to escape strange characters

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

# Returns if the text is valid or not
def validInputText(inputtext):
	# Need to escape special characters

	inputtext = inputtext.strip()
	if(inputtext=="" or inputtext==None):
		return False
	else:
		return True

# Utility function to create a query segment from advanced search form
# first is a boolean that says whether the current segment is the first segment in their query
def createQuerySeg(x, first):
	querySeg = ""
	negation = ""

	# # Name of each input field
	# category = 'category1'
	# contains = 'contains1'
	# inputtext = 'inputtext1'
	# condition = 'condition1'

	# Name of each input field
	categoryx = 'category' + str(x)
	containsx = 'contains' + str(x)
	inputtextx = 'inputtext' + str(x)
	conditionx = 'condition' + str(x)

	# Get values from submitted form
	categorystring = request.form[categoryx]
	containsCond = request.form[containsx]
	inputtext = request.form[inputtextx]
	condition = request.form[conditionx]

	# Filter the condition (not, and, or)
	convertedCond = convertCond(condition)

	# Convert the condition to query language
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

		# Take the values and convert to model atribute names
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
		# else if for DATE - needs to be done
		elif(categorystring == 'DateCreated'):
			querySeg += ('Q()')
		else:
			querySeg += ("Q(" + categorystring + negation + "__" + 
			containsCond + " ='" + inputtext + "')")
	return querySeg

# Handler for advanced search url request
@main.route('/advancedSearch', methods=['GET', 'POST'])
def advancedSearch():

	# If the request made is a POST request
	if request.method == 'POST':
		try:

			# If the button "RefineList" was the one that sent the request
			if(request.form['submitBtn']=='RefineList'):

				# Call refineList
				return refineList(request, "adv")

			# If the request was from "Export" button
			elif request.form['submitBtn']=='Export':

				# Call downloadResults
				return downloadResults(request.form)
		except:	

			# Get 'preferences' cookie
			preferences = request.cookies.get('preferences')

			# If the cookie doesnt exist 
			if not preferences: 

				# Return default preferences
				preferences = default_pref

			else:

				# Otherwise convert the cookie to a python object
				preferences = json.loads(preferences)

			cond = 'condition1'
			first = True

			# get number of conditions
			count = int(request.form['count'])

			# string to contain the mongo query
			query = 'lit = Lit.objects('

			# go through all the conditions and add the information to 
			for x in xrange(1, count+1):

				condx = str.replace(cond, '1', str(x))

				# check if the condition is ignore
				if( request.form[condx] != 'ignore' ):
					print "checking for ignore"

					# if not ignore then add the information to the mongo query
					# get the information from the 4 input fields
					temp = createQuerySeg(x, first)
					if(temp != None and temp != ''):
						query += temp
						first = False

			query += (')')
			print "query is :" + query

			if( len(query) != 19 ):
				
				# Execute query
				exec query

				# print json.dumps(lit)
				# lit = Lit.objects(Q(author__iexact = 'bob') | Q(keywords__icontains = 'only'))
				# print json.dumps(lit)

				if( len(lit) != 0 ):

					# Convert lit to appropiate list object
					jsonlit = litToJson(lit)
					lit = json.loads(jsonlit)
					lit = convertId(lit)
					sessioninfo = json.dumps(request.form)

					# Render advanced search page
					return render_template('AdvancedSearch.html', lit = lit, sessioninfo = sessioninfo, preferences = preferences)
				
				# Otherwise there were no results
				else:
					flash("Your query had no results.")
					sessioninfo = json.dumps(request.form)
					return render_template('AdvancedSearch.html', sessioninfo = sessioninfo, preferences = preferences)

 	return render_template('AdvancedSearch.html')

#####################
# User Profile Page #
#####################

# Display user's profile
# name in the url route is a variable that contains the user's name
@main.route('/user/<name>')
def user(name):

	# Retrieve user from db
	user = User.objects(name__iexact = name).first()

	# Sort and save the latest 5 changed the user has made
	latest_activity = user.u_edit_record
	latest_activity = sorted(latest_activity, key=lambda la: la.date, reverse=True)
	latest_activity = latest_activity[0:5]

	return render_template('user.html', user = user, latest_activity = latest_activity)


#################
# Lit Main Page #
#################

# Display the literature
# lit_id in the url route is a variable, contains the literature's id
@main.route('/lit/<lit_id>')
def lit(lit_id):

	# Retrieve the id
	lit = Lit.objects(id__iexact = lit_id).first()

	# If the lit does not exist send a 404 response
	if lit is None:
		abort(404)

	return render_template('lit.html', lit = lit)


###########
# Add Lit #
###########

# Add literature
@main.route('/addLit', methods=['GET', 'POST'])
@login_required
def addLit():

	# Create new add lit form
 	form = AddLitForm()

 	# On form submission
 	if form.validate_on_submit():

 		# If the literature is already in the database, then do not add the material, return
		lit = Lit.objects(title__iexact = form.title.data, author__iexact = form.author.data, pages__iexact = form.pages.data).first()
		if lit is not None:
 			flash("This is already in the DB. This is the page")
			return render_template('lit.html', lit = lit)

		# Create a new lit object, save to db first, then update fields
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

		# Add user's edit in edit history
		editHist = LitEditRecord(lastUserEdited = current_user.name)

		# If the link field is not empty, save the link too
		# If statement is done because update fails when attempting to save an empty string
		if form.link.data is not None:
			lit.update(set__link = form.link.data)
		
		# Add keywords into the db as a listField
		keywordslist = (form.keywords.data).split(",")
		for x in range(0, len(keywordslist)):
			key = str(keywordslist[x].strip())
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

# Update literature 
@main.route('/updateLit/<lit_id>', methods=['GET','POST'])
@login_required
def updateLit(lit_id):

	# Get lit object by id
	lit = Lit.objects(id__iexact = lit_id).first()

	# Create new add lit form ( also used as an update lit form )
	form = AddLitForm(None, lit)

	# Join the keywords into a string and set the form to contain this
	keywordslist = ', '.join(lit.keywords).encode('utf-8')
	form.keywords.data = keywordslist

	# Return the update page
	return render_template('update.html', form = form, lit = lit)

#################
# Submit Update #
#################

# When user submits the update lit form ( Could be combined with the updateLit method )
@main.route('/updateLitSub/<lit_id>', methods=['POST'])
@login_required
def updateLitSub(lit_id):
	form = AddLitForm()
	lit = Lit.objects(id__iexact = lit_id).first()

	# Update all the fields of the object ( Could possibly be done in a simpler fashion )
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

		# Clear the objects keywords
		lit.update(set__keywords = [])

		# Separate the keywords field string by comma
		keywordslist = (form.keywords.data).split(",")

		# Push each key into the obj list field 
		for x in range(0, len(keywordslist)):
			key = str(keywordslist[x].strip())
			if key is not None :
				lit.update(push__keywords = key)

		# Add new Lit history obj
		editHist = LitEditRecord(lastUserEdited = current_user.name)
		lit.update(push__l_edit_record=editHist)
		lit.update(set__last_edit = editHist)
		lit.reload()

		# Add new User edit history obj
		userHist = UserEditRecord(litEdited = str(lit.id), operation = "update", litEditedTitle = lit.title)
		current_user.update(push__u_edit_record=userHist)
		current_user.reload()

		lit = Lit.objects(id__iexact = lit_id).first()
		flash(lit.title + " has been updated")
	else:
		flash(lit.title + " failed to be updated")
	return render_template('lit.html', lit = lit)

######################
# Edit Preferences 
######################

# Default user preferences for search result fields display
default_pref = {"author": True, "yrPublished": True, "title":True, "sourceTitle": True, "primaryField": True, "creator": True, "dateCreatedOn": True, "editor": False, "refType": False, "lastModified": False, "lastModifiedBy": False}

class Struct:
    def __init__(self, **entries): 
        self.__dict__.update(entries)

@main.route('/edit-pref', methods=['GET', 'POST'])
def preferences():
 	form = Preferences()
 	
 	# If the user is logged in, take their preferences
	if current_user.is_authenticated():
		preferences = {"author": current_user.author, "yrPublished": current_user.yrPublished, "title":current_user.title, "sourceTitle": current_user.sourceTitle, "primaryField": current_user.primaryField, "creator": current_user.creator, "dateCreatedOn": current_user.dateCreatedOn, "editor": current_user.editor, "refType": current_user.refType, "lastModified": current_user.lastModified, "lastModifiedBy": current_user.lastModifiedBy}
 	else:
 		# Get cookie containing pref
 		preferences = request.cookies.get('preferences')
		if preferences:
			preferences = json.loads(preferences)

 	# If user does not have pref, give default
	if not preferences:
		preferences = default_pref

	# Debugging
	# print "GOT PREFERENCE"
	# for item in preferences:
	# 	print item + " "  + str(preferences[item])
	# print "END PREFERENCES FROM COOKIE"

	# If form is being submitted
 	if form.validate_on_submit():

 		# Create a dict from preferences in the form 
 		for attr in form:
 			preferences[attr.name] = attr.data 
		preferencesobj = Struct(**preferences)
 		form = Preferences(None, obj=preferencesobj)

 		# If user is logged in, save preferences to the db
 		if current_user.is_authenticated():
	 		current_user.update(set__title = form.title.data)
	 		current_user.update(set__author = form.author.data)
	 		current_user.update(set__primaryField = form.primaryField.data)
	 		current_user.update(set__editor = form.editor.data)
	 		current_user.update(set__yrPublished = form.yrPublished.data)
	 		current_user.update(set__refType = form.refType.data)
	 		current_user.update(set__creator = form.creator.data)
	 		current_user.update(set__dateCreatedOn = form.dateCreatedOn.data)
	 		current_user.update(set__lastModified = form.lastModified.data)
	 		current_user.update(set__lastModifiedBy = form.lastModifiedBy.data)
	 		flash('Your preferences have been saved')

	 	# Otherwise save their preferences to their browser as a cookie
 		else:
 			flash('Your preferences have been saved for your session')
			response = make_response(render_template('preferences.html', form=form))
	 		response.set_cookie('preferences', json.dumps(preferences))
			return response

 	# If no form is submitted, return the form prefilled with old preferences
	preferencesobj = Struct(**preferences) 	
 	form = Preferences(None, preferencesobj)
 	return render_template('preferences.html', form=form)

################
# Edit Profile #
################

# Edit profile
@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileForm()

	# On form submit, update profile information
 	if form.validate_on_submit():
 		current_user.update(set__name=form.name.data)
 		current_user.update(set__location=form.location.data)
 		current_user.update(set__credentials = form.credentials.data)
 		current_user.update(set__description = form.description.data)
 		flash('Your profile has been updated.')
 		return redirect(url_for('.user', email = current_user.email))

 	# If no submission, return form prefilled with current user profile information
 	form = EditProfileForm(None, current_user)
 	return render_template('editProfile.html', form=form)
 

# Not currently in use ##############################################################

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
 	
 	
