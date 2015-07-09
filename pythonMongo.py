# pythonMongo.py
# Author: Riley
# Date: July 7, 2015
# Purpose: To come up with a base that can do various
# things in Python with MongoDB

from pymongo import MongoClient

######################
#
# Fuzzy Search
#
######################
# db is a reference to the proper collection
# fieldName should be a string giving a field in the data
# pattern should be a string pattern for a regex
"""def fuzzySearch(db, fieldName, pattern):
	results = db.find({fieldName: { $regex: pattern} }, 
		projection = {'tags': False}, 
		limit = 100)
	return results"""
	
#######################
#
# Strict Search
#
#######################
# lookupValue is a value for a stricter search
def strictSearch(db, fieldName, lookupValue):
	results = db.find({fieldName: lookupValue}, 
		projection = {'tags': False}, 
		limit = 100)
	return results
	

#######################
#
# Proper Insert
#
#######################
# Record is a dictionary of the value to insert, should contain refType, title, author, description
def insert(db, record):
	if (record["refType"] is None | record["title"] is None | record["author"] is None | record["description"] is None):
		print "Error, entry must include the reference type, title, author, and description at least."
		return
	db.insert_one(record)


######################
#
# Proper Delete
#
######################

"""def delete(db, fieldName, pattern):
	results = db.find({fieldName: { $regex: pattern}})
	for i in range(len(results)):
		print i+1, ":", results[i]
	choice = raw_input("Select the number of the object you wish to delete: ")
	while !choice.isdigit() & int(choice) < 1 & int(choice) > len(results):
		choice = raw_input("Please enter the number of the object you wish to delete: ")
		choice = int(choice)
	objToDelete = results[choice-1]["_id"]
	result = db.delete_one({_id: objToDelete})
	print "Successful Delete"""

#######################
#
# Proper Update
#
#######################
# Pattern refers to a search for the object you actually wanna update
"""def update(db, fieldName, pattern):
	results = db.find({fieldName: { $regex: pattern}})
	for i in range(len(results)):
		print i+1, ":", results[i]
	choice = raw_input("Select the number of the object you wish to delete: ")
	while !choice.isdigit() & int(choice) < 1 & int(choice) > len(results):
		choice = raw_input("Please enter the number of the object you wish to delete: ")
		choice = int(choice)
	objToUpdate = results[choice-1]["_id"]
	
	## In real life this will take input from the HTML, for now, we wing it
	result = db.update_one({_id: objToUpdate}, {'edition': '5'})"""	


if __name__ == '__main__':
	# connect to the MongoDB on MongoLab
	connection = MongoClient("mongodb://mikachama:Haruka10@ds033419.mongolab.com:33419/inventory")

	# connect to the literature collection
	db = connection.inventory.literature

	# create dictionary
	book_record = {}

	# set count
	count = 0

	# loop for data input 10 times
	while (count < 10):
   		# ask for input
   		book_type = raw_input("Enter type of literature, select from journal, textbook, article, magazine, other: ")
   		while book_type not in ['journal', 'textbook', 'article', 'other', 'magazine']:
   			book_type = raw_input("Not included. Please select from journal, textbook, article, magazine, other: ")
   
   		book_title = raw_input("Enter title: ")
   		book_author = raw_input("Enter author: ")
   		book_edition = raw_input("Input edition, enter -1 if no edition available: ")
   		book_YrPublished = raw_input("Enter year published, -1 if unknown: ")
   		book_desc = raw_input("Describe the literature: ")
   		book_tags = raw_input("Tag the literature: ").split(",")
   
   		# place values in dictionary
   		book_record = {'refType': book_type, 'title': book_title, 'author': book_author, 'edition': book_edition, 
   		'yrPublished': book_YrPublished, 'description': book_desc, 'tags': book_tags}
   
   		# insert the record
   		db.insert(book_record)
   		count = count + 1

# find all documents
results = db.find()

print('+-+-+-+-+-+-+-+-+-+-+-+-+-+-')

# display documents from collection
for record in results:
# print out the document
	print record

# close the connection to MongoDB
connection.close()
