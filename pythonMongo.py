# mongo_hello_world.py
# Author: Bruce Elgort
# Date: March 18, 2014
# Purpose: To demonstrate how to use Python to
# 1) Connect to a MongoDB document collection
# 2) Insert a document
# 3) Display all of the documents in a collection

from pymongo import MongoClient

# connect to the MongoDB on MongoLab
# to learn more about MongoLab visit http://www.mongolab.com
# replace the "" in the line below with your MongoLab connection string
# you can also use a local MongoDB instance
connection = MongoClient("mongodb://mikachama:Haruka10@ds033419.mongolab.com:33419/inventory")

# connect to the literature collection
db = connection.inventory.literature

# create dictionary
book_record = {}

# set flag variable
flag = True

# loop for data input
while (flag):
   # ask for input
   book_type = input("Enter type of literature, select from journal, textbook, article, magazine, other: ")
   while book_type not in ['journal', 'textbook', 'article', 'other', 'magazine']:
   	book_type = input("Enter type of literature, select from journal, textbook, article, magazine, other: ")
   
   book_title = input("Enter book title: ")
   book_author = input("Enter book author: ")
   book_edition = input("Input edition, enter -1 if no edition available: ")
   book_
   # place values in dictionary
   book_record = {'refType': book_type, 'title': book_title, 'author': book_author, 'edition': book_edition}
   # insert the record
   db.insert(book_record)
   # should we continue?
   flag = input('Enter another record? ')
   if (flag[0].upper() == 'N'):
      flag = False

# find all documents
results = db.find()

print('+-+-+-+-+-+-+-+-+-+-+-+-+-+-')

# display documents from collection
for record in results:
# print out the document
	print(record['title'] + ',',record['author'])

# close the connection to MongoDB
connection.close()
