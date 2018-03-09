import face_recognition
import cv2
import numpy as np
from os import listdir, remove, rmdir, makedirs
from os.path import isdir, join, isfile, splitext,exists
from face_recognition.cli import image_files_in_folder
from face_recognition import face_locations
import time
import cPickle as pickle
import threading
import boto3
import MySQLdb
import shutil


import urllib, cStringIO
from PIL import Image, ImageEnhance
from texttable import Texttable

import store
import gather

train_dir = "faces/"
num_people = -1
USERNAME = ''
PASSWORD = ''
DB_NAME = ''

print "Connecting to RDS instance"

#Insert host url from RDS
conn = MySQLdb.connect (    host = '',
                            user = USERNAME,
                            passwd = PASSWORD,
                            db = DB_NAME, 
                            port = 3306
                        )

print "Connected to RDS instance"
cursor = conn.cursor ()


#constants
datafile = "faces/faces.dat"

video_capture = cv2.VideoCapture(0)
verbose = True

timeStart = time.time()

known_face_encodings = []
known_face_names = []

with open(datafile, "r") as f:
    known_face_encodings = pickle.load(f)
    known_face_names = pickle.load(f)


# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

t = None
count = 0
def updateFaces():
    updated = False;
    global t
    global known_face_encodings
    global known_face_names
    global num_people
    global conn
    cloud_people = []
    print(cloud_people)
    cursor = conn.cursor()
    train_dir = "faces/"

    cursor.execute("SELECT * FROM People")
    rows = cursor.fetchall()
    conn.commit()
    len_people = len(rows)
    print("Number of people in database : " + str(len_people))
    if (len_people != num_people):
        for row in rows:
            directory = join(train_dir, row[1].lower())
            cloud_people.append(directory)

            if not exists(directory):
                makedirs(directory)
                print(directory)
                file = cStringIO.StringIO(urllib.urlopen(row[2]).read())
                img = Image.open(file)
                img.save(directory + "/" + row[1].lower().strip() + ".png")
        print(cloud_people)

        for d in listdir(train_dir):
            d = join(train_dir, d)
            if isdir(d):
                if d not in cloud_people:
                    shutil.rmtree(d, ignore_errors=True)

    if (len_people != num_people):
        print("Updating local directory!   ")
        store.storeFaces()
        with open(datafile, "r") as f:
            known_face_encodings = pickle.load(f)
            known_face_names = pickle.load(f)
        num_people = len_people

    print("Resetting Thread")
    t = threading.Timer(4.0, updateFaces)
    t.start()

updateFaces()

while True:
    # Grab a single frame of video
    ret, frame = video_capture.read()

    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Only process every other frame of video to save time
    if process_this_frame:
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.48)
            name = "Unknown"

            # If a match was found in known_face_encodings, just use the first one.
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]

            face_names.append(name)

    process_this_frame = not process_this_frame


    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        if (name != "Unknown"):
            # Draw Green rectangle
            cv2.rectangle(frame, (left, top), (right, bottom), (124,252,0) , 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (124,252,0), cv2.FILLED)
           
        else:
            cv2.rectangle(frame, (left, top), (right, bottom), (0,0,255) , 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0,0,255), cv2.FILLED)
        
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)


    # Display the resulting image
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

t.cancel()
# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()