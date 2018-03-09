import face_recognition
import cv2
import numpy as np
from os import listdir, remove, rmdir
from os.path import isdir, join, isfile, splitext
from face_recognition.cli import image_files_in_folder
from face_recognition import face_locations
import time
import cPickle as pickle

def storeFaces():
    datafile = "faces/faces.dat"

    # Parses through file structure for faces
    known_face_encodings = []
    known_face_names = []
    train_dir = "faces/"
    for class_dir in listdir(train_dir):
        if not isdir(join(train_dir, class_dir)):
            continue
        if not listdir(join(train_dir,class_dir)):
            rmdir(join(train_dir,class_dir))
            continue
        for img_path in image_files_in_folder(join(train_dir, class_dir)):
            image = face_recognition.load_image_file(img_path)
            faces_bboxes = face_locations(image)
            if len(faces_bboxes) != 1:
                remove(img_path)
                if verbose:
                    print("image {} not fit for training: {}".format(img_path, "didn't find a face" if len(faces_bboxes) < 1 else "found more than one face"))
                continue
            known_face_encodings.append(face_recognition.face_encodings(image, known_face_locations=faces_bboxes)[0])
            known_face_names.append(class_dir)
        print(len(known_face_names))
        if (len(known_face_names) > 10000):
            break


    known_face_encodings = np.array(known_face_encodings)

    # Open datafile and store the two lists, seperately
    with open(datafile, "w") as f:
        pickle.dump(known_face_encodings, f,protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(known_face_names, f,protocol=pickle.HIGHEST_PROTOCOL)

