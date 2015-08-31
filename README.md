# OBET
======

#### A library site made in Python using the Flask framework.

**Creator Notes:** *This README will contain a detailed set of basic instructions on working this site, with the assumption that the person to take it over is a junior or senior CS student with little to no knowledge of full stack web application development.*

OBET was built in Ubuntu (Linux/Unix), and it's suggested that the 
new student to upkeep it have experience with navigating the command line,
though it is not necessary for the student to know too much more than
what is taught in the first level C++ class.

It is also suggested to have a Linux build, or the ability to [boot one from a
flash drive]. (http://www.ubuntu.com/download/desktop/create-a-usb-stick-on-ubuntu)

**Note:** *This can be done on a Mac (with some foibles) or on a Windows (with some
difficulties) build, but the student will have to look that up personally.*


### Work Setup
======
Before beginning, the computer should be prepared with python and a python installer.

##### Install Python
	* The version used for this site is 2.7.6
	* Ubuntu 14.04 comes with Python 3.4 installed
	
Open a terminal/console and type:
`sudo apt-get install build-essential checkinstall`
`sudo apt-get install libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev`
This globally installs necessary dependencies.

`sudo` makes the installation global, and may require a password from you.
`apt-get` grabs the applications you want to install.
`install` is self-explanatory and following that are the list of items you want to install, separated by a space.

There are a ton of different ways to install Python, particularly if you want Python 2.7,
and they can be easily found by looking up installation of Python.

##### Install pip
	* pip is a package installer for Python packages. It will make your life much easier.

In the console, type:
`sudo apt-get install pip` -- installs pip globally
	
##### Install git if you don't have it, make a github account, grab the code from the repo.
	* Git is a command line version control system that allows you to keep track of your code.
	* Github allows you to store your code elsewhere so it's never lost no matter what.

In the console, type:
`sudo apt-get install git` -- installs git globally
`cd OBET` -- switches to a folder called OBET if it exists, otherwise makes one and switches there.
`git init` -- starts the folder as a git project

After making an account on github, go [here] (https://github.com/techiecheckie/OBET/) and [fork, then clone the project] (https://guides.github.com/activities/forking/).

To connect to github from your computer, you will need to [generate and add an SSH key] (https://help.github.com/articles/generating-ssh-keys/) to be allowed to do so.

Back in the console, type:
`git remote add upstream git@github.com:techiecheckie/OBET.git` -- this creates a connection to the repo

Finally, to pull the code from the repo into your folder, type in the console:
`git fetch upstream` -- this grabs the aforementioned connection
`git merge upstream/master` or `git pull upstream master` -- this merges and/or pulls the code from the repo

To use the repo and submit your changes later on, navigate to the appropriate folder in the command line.
There are 3 steps to push your changes to the github repo.
1. `git add changedFileName.ext` -- this tells git that you plan to commit this file. There are many files that you will not want to commit to the repo. ONLY commit .py files, .html files, .md files, image files associated with the site (jpg, ico, png, and so on), and any .txt files, if you add them. (In this case, it's adding a fake file called changedFileName.ext, you should replace that with what you w
	* **DO NOT commit anything in the venv folder to the repo.**
	* **DO NOT commit .py~, .pyc, .pyc~, or any other file ending in ~ to the repo.**
	* You may notice that adding things one by one will get very tedious...absolutely. You can add a [.gitignore file] (https://help.github.com/articles/ignoring-files/) to avoid including unwanted files.
2. `git commit -m "Message about what to commit."` -- this commits your new code to the local repo created by git on your computer. *It has not yet been pushed to your github.* Your message should detail what you're adding fairly well, for other users.
3. `git push` -- the final step that will push to github.

If interested, read up on [git] (https://git-scm.com/download/linux) and [github] (https://help.github.com/articles/set-up-git/).

##### Install virtualenv.
	* Virtualenv makes a virtual environment on your computer that will allow you to install certain python packages, but only within a specific folder. It essentially protects your main python installation.
	
In the console, type:
`pip install virtualenv` -- installs virtualenv
`cd OBET` -- navigate to the appropriate directory with your project, whatever its name.
`virtualenv venv` -- creates a virtual environment with the name you give it, in this case venv

Read more about [virtualenv] (http://docs.python-guide.org/en/latest/dev/virtualenvs/) if you are interested or having trouble.

##### Install a text editor if you don't have one. (Optional)
	* gedit was used, and sublime text is another good one.
	* if you're having trouble with the command line, you can simply google and download the package and install through the Ubuntu GUI.

##### Start your virtual environment and install the necessary dependencies.

In the console, type:
`source venv/bin/activate` -- activates your virtual environment. You should notice (venv) appear before your command prompt, that's the sign you're doing it correctly.
`pip install -r requirements.txt` -- installs requirements needed to run the project within your environment

##### Get the environment variables set up. (More on this later.)

##### Run the application if all has worked out!

In the console, navigate to the root folder of the project and type:
`python manage.py runserver -dr` -- this starts the app and the server. The -dr parameters that allow 2 different things.
	* -r will instantly reload the server whenever you make a change to a .py file, so you don't have to keep running this command when you make changes.
	* -d runs the server in debug mode so that you will get full traceback of errors in the browser when something goes awry.

You should see a message in the console:
 ```* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 	* Restarting with stat```

Or something similar. The link tells you what you need to enter into your browser to make the site run.

Open a browser and type "localhost:5000", and the site should come alive.

##### Congrats! You are ready to begin developing!


### Code Navigation Overview
======

###### Main Site Folder
* The actual application is in the "app" folder.
* Tests are inside "tests"
* Venv you already know.
* requirements.txt lists the requirements for easy dependency install on new builds.
* config.py has configuration settings.
* manage.py launches the application.

###### App Folder
1. Root
	* Auth stores the information that goes into user authorization and email confirmation.
	* Main stores the general logic and routing of the site.
	* Static stores images and stylesheets associated with the project.
	* Templates stores your HTML files.
	* decorators.py holds the code needed to do quick permissions checking for a particular page on the site.
	* email.py holds code to send email confirmations.
	* \__init__.py has the code to start up the application.

2. Auth
	* \__init__.py stores the startup for the Blueprint module.
	* forms.py holds forms that need authorization of some kind.
	* views.py is where views that need authorization are stored.
	
3. Main
	* \__init__.py stores the startup for the Blueprint module as well as injecting permissions.
	* errors.py holds the routing for errors, either from the site or the server.
	* forms.py holds the forms associated with the main workings of the site.
	* views.py holds the views for the main site processes.
	
4. Static and Templates
	* favicon.ico is simply the name of the icon that goes next to the site name in the browser.
	* ________.html is the HTML page that will show up when views.py calls them.

###### Tests Folder
* test_basics.py holds code to test the connection to the database.
* test\_user_model.py allows you to test to make sure the parts of the User model are working.


### Important Information
======

* The back end uses [MongoDB] (https://www.mongodb.org/) for its database, using the [flask-mongoengine] (https://flask-mongoengine.readthedocs.org/en/latest/)/[MongoEngine] (https://mongoengine-odm.readthedocs.org/) libraries to connect to a [MongoLab] (https://mongolab.com/) account. These are important reads to help you understand the working of the database.

* The front end uses a Python framework called [Flask] (http://flask.pocoo.org/docs/0.10/). Flask has numerous libraries, so the main site is not the best to get specific information. Instead, you should look up the specific libraries of Flask, which can be found in the requirements.txt file. The relevant lines will begin with Flask-libraryName.

* If you need to install or update modules for your new functionality, be sure to save them into the requirements.txt. This can be auto-generated with the command `pip freeze > requirements.txt`. This makes it easier for the next developer.

### Suggestions
======
##### READ THIS CAREFULLY

###### These are included to make website development not only easy for you, but easy for all those that come after you to work on it. It also includes good skills for development on any project with multiple people, and will come in handy in your future workplace.

* Comment your code. _Comment your code._ **Comment your code.** COMMENT YOUR CODE. _COMMENT YOUR CODE._ **COMMENT YOUR CODE FOR THE LOVE OF ALL THAT IS GOOD AND HOLY!**

* As you look through the code, you will notice certain stylistic choices. These may be in naming variables of different types, folders and files, but they may also just be ways of writing, spacing, and commenting the code. Keep your code in line with them. It will make things much easier to read and more intuitive for new devs.

* Python is a language that pays absolute attention to spacing and tabbing. That makes it much easier to read, since many times you will be unable to stick multiple things on the same line. However, other types of spacing are also important. As said above, look at the code already given and imitate the style to keep the code readable for everyone!

* Many errors will come up as you work. The best way to address them is to google them! Stackoverflow can answer a large number of questions!

* Knowing Python syntax and the syntax of your libraries is important here. You may have a simple error caused by bad syntax. Check the console; it will print the traceback of the error for you.

* If the console says it cannot import some module? Check your import statements! In some cases, order DOES matter to prevent circular issues.

* Learn to do a good writeup of any issues you are having. A good problem inquiry generally involves the following:
	* A picture, explanation, or cut-and-paste of the exact error or problem. Screenshooting should be your friend to use liberally. Explanations are your *last resort* and should only done in the case that you cannot take a picture or directly cut and paste an error message.
	* A detailed list of steps on how the problem came about. This may mean an explanation on how to cause the problem/error to occur, what you believe caused the problem, or what you were doing when the problem occurred. Include any commands you may have run or changes you may have made.
	* If relevant, a basic rundown of the structure of the code. This is usually used to explain what certain variables are or what they are supposed to be doing/storing.



### Resources
======

* **The book _Flask Web Development_ by Miguel Grinberg is THE number 1 resource for detailed insight into the vast majority of this site! You should read as much as you can before starting development.**

* For the information NOT included in the Flask book, Stackoverflow will be your best friend.

* In addition to the links above, you may want to consider searching on:
	* navigating the command line
	* using Ubuntu
	* installing Python and Python dependencies on Ubuntu
	* the Flask libraries included in the requirements.txt
	* getting the website to run locally on a Windows/Mac machine
	* using Git and Github effectively with a group of people, including starting your own Git project, rolling back to previous commits in case something breaks, how to fix merging issues, creating various versions of your project to show the process or test new things on, making pull requests to other code through Github, and using Github's issues and milestones to keep track of problems and future tasks.
	* changing from the MongoLab account to a DB stored on your own server
	* database migration
	* various types of unit testing

* If you are still having trouble, please contact the creator of this site at **techiecheckie@gmail.com**.


