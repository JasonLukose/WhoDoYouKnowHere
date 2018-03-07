from texttable import Texttable
import MySQLdb
import boto3
import time
import requests
from flask import Flask, jsonify, abort, request, make_response, url_for
from flask import render_template, redirect
import serial
import sys
from awscredentials import USERNAME,PASSWORD,DB_NAME,AWS_KEY,AWS_SECRET,REGION,BUCKET
import cv2


s3 = boto3.client('s3', aws_access_key_id=AWS_KEY,
                            aws_secret_access_key=AWS_SECRET)

app = Flask(__name__)
@app.route('/')
def intro():
	return render_template('intro.html')


@app.route('/attendees', methods=['GET'])
def display():
    conn = MySQLdb.connect (    host = "",
                            user = USERNAME,
                            passwd = PASSWORD,
                            db = DB_NAME, 
                            port = 3306
                        )
    cursor = conn.cursor ()
    cursor.execute("SELECT * FROM People")
    rows = cursor.fetchall()
    diction = {
                
        }
    diction2 = {
                
        }   
    for row in rows:
        diction[row[1]] = [row[2], row[0]]

    cursor.close()
    conn.close()
    return render_template('showData.html',your_list=diction)


@app.route('/add', methods=['GET', 'POST'])
def course_add_page():
    if request.method == 'POST':
    	
        result = request.form
        print(result)
        
        #s3 = boto3.client('s3', aws_access_key_id=AWS_KEY,aws_secret_access_key=AWS_SECRET)
        filenameWithPath = "/home/ubuntu/final/static/" + request.form['Picture']
        path_filename=request.form['Picture']
        s3.upload_file(filenameWithPath, BUCKET, path_filename)
        s3.put_object_acl(ACL='public-read', Bucket=BUCKET, Key=path_filename)

        conn = MySQLdb.connect (    host = "",
                            user = USERNAME,
                            passwd = PASSWORD,
                            db = DB_NAME, 
                            port = 3306
                        )
        print("Connected to RDS instance")
                                
        cursor = conn.cursor ()
        cursor.execute ("SELECT VERSION()")
        row = cursor.fetchone ()
        print("server version:", row[0])

        formUrl = "https://hackgt.s3.amazonaws.com/" + path_filename
    
        statement = "INSERT INTO People(pId, Name, Picture, Duration) VALUES ("+\
        request.form['pId']+", '"+\
        request.form['Name']+"', '"+\
        formUrl+"', '"+\
        request.form['Duration']+"');";

        print(statement)
        cursor.execute(statement);
        conn.commit()
        cursor.close()
        conn.close()
        
        return redirect('/attendees')

    else:
        return render_template('add.html')

@app.route('/delete/<int:student_id>', methods=['GET'])
def delete_process(student_id):
    conn = MySQLdb.connect (    host = "",
                            user = USERNAME,
                            passwd = PASSWORD,
                            db = DB_NAME,
                            port = 3306
                            )
    print("Connected to RDS instance")
                            
    cursor = conn.cursor ()
    cursor.execute ("SELECT VERSION()")
    row = cursor.fetchone ()
    print("server version:", row[0])
    cursor.execute("DELETE FROM People WHERE pId="+str(student_id)+";");
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect('/attendees')

if __name__ == '__main__':
        app.run(host='0.0.0.0', port=80)