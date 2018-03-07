import urllib, cStringIO
from PIL import Image, ImageEnhance
import boto3
import MySQLdb
from texttable import Texttable
from os import listdir, remove, rmdir,makedirs
from os.path import isdir, join, isfile, splitext, exists

train_dir = "faces/"

def populateLocal(cursor, num_people):
	cursor.execute("SELECT * FROM People")
	rows = cursor.fetchall()
	len_people = len(rows)
	print("len rows" + str(len_people))
	if (len_people != num_people):
		for row in rows:
			directory = join(train_dir, row[1].lower())
			
			if not exists(directory):
				makedirs(directory)
				print(directory)
				file = cStringIO.StringIO(urllib.urlopen(row[2]).read())
				img = Image.open(file)
				img.save(directory + "/" + row[1].lower().strip() + ".png")
	
	return (len_people, len_people != num_people)




