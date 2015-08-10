from datetime import datetime
from flask import render_template, session, redirect, url_for, flash
from . import main
from .forms import NameForm, SearchForm#, AddLitForm
from .. import db
from ..models import User, Role, Lit
from flask.ext.login import login_required, current_user


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

@main.route('/search', methods=['GET', 'POST'])
def search():
 form = SearchForm()
 if form.validate_on_submit():
 	## Build a query object
 	lit = Lit.objects(title__icontains = form.title.data)
 	if len(lit) == 0:
 			flash("Your search returned nothing. Try typing parts of fields you know.")
 	else:
 		return render_template('search.html', form = form, lit = lit)
 	return redirect(url_for('main.search'))
 return render_template('search.html', form = form)


@main.route('/exactSearch', methods=['GET', 'POST'])
def exactSearch():
 form = SearchForm()
 if form.validate_on_submit():
 	## Build a query object
 	lit = Lit.objects(title__iexact = form.title.data)
 	if len(lit) == 0:
 			flash("Your search returned nothing. Try being less specific.")
 	else:
 		return render_template('exactSearch.html', form = form, lit = lit)
 	return redirect(url_for('main.exactSearch'))
 return render_template('exactSearch.html', form = form)


#from ..decorators import admin_required, permission_required, user_required
#@main.route('/<name>/addLit')
#@login_required
#@user_required
#def addLit():
#	isUpdate = False
# 	form = AddLitForm()
# 	if form.validate_on_submit():
# 		## Build a query object
#		lit = Lit.objects().first()
#		if lit is not None:
# 			flash("This is already in the DB. Updating instead.")
#			isUpdate = True
#		lit = Lit(refType = form.refType.data, title = form.title.data, author = form.author.data, description=form.description.data)
#		lit.save()
#		if isUpdate:
#			flash("Updated the entry.")
#		else:
#			flash("Added new entry to the DB.")				
# 		return redirect(url_for('main.addLit'))
# 	return render_template('addLit.html', name = current_user.name, form = form)

#changeEmail
#changePass

 
#@main.route('/<name>/whateverwhatever')
#@login_required
#@admin_required
#deleteLit
#deleteUser
