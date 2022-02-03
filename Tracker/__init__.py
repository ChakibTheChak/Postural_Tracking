#Library  ##################################################################################################################################
#Flask 
from distutils.log import error
from click import echo
from flask import Flask , render_template,Response ,request, template_rendered,redirect ,url_for , flash , get_flashed_messages,session
from flask_sqlalchemy import SQLAlchemy 
from flask_bcrypt import Bcrypt
from flask_login import LoginManager ,  login_user ,logout_user,login_required, current_user
from flask_executor import executor
# Threading for futur use
from threading import Thread
# SQL and DB
import mysql.connector 
from sqlalchemy_utils.functions import database_exists ,create_database
from sqlalchemy.exc import IntegrityError
# Camera and vision library
import  cv2
import numpy as np
import datetime,time
# Tracking Library
import mediapipe as mp
import os 

# Global variables ###############################################################################################################################
mp_drawing=mp.solutions.drawing_utils
mp_position=mp.solutions.pose

# Get env variable from the docker else put localhost 
DB_HOST=os.environ.get('DB_HOST', default="localhost")
#Instantiate Flask app
app=Flask(__name__,template_folder='./templates')
app.config['SECRET_KEY']='b0ed6889a79c58207a6874f8'
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:password@{DB_HOST}:3306/posturaltracker'.format(DB_HOST=DB_HOST)

db=SQLAlchemy(app)
bcrypt=Bcrypt(app)
login_manager=LoginManager(app)
login_manager.login_view="login_page"
login_manager.login_message_category="info"
from Tracker import models
from  Tracker import routes

# Manage the SQL LITE File checking / exist and recreate if uninstalled 
if database_exists(str(db.engine.url)):
    print("Data base exists")
    db.create_all()
    try:
        base_Settings=models.Settings.query.get(1)
        base_User=models.User.query.get(1)
        base_Track=models.Track.query.get(1)
        print ("Table ID found :",base_User,base_Settings,base_Track)
    except error as e :
        db.session.add(models.Settings(capture=0,rtsp_user="admin",rtsp_pw="admin",rtsp_ip="192.168.1.1",rtsp_port="554",rtsp_channel="1",rtsp_path="",rtsp_custom="",stream_mode=0,owner=1))
        db.session.add(models.User(username="admin",email_address="chakib.mouhoubi@gmail" ,password="administrator"))
        db.session.add(models.Track(detection_confidence=0.5,tracking_confidence=0.5))
        db.create_all()
        db.session.commit()
        print ("Error Message:",e)    
    
else :
    print ("Data base does not exist and will be created for you")    
    create_database(db.engine.url)       
    db.session.add(models.Settings(capture=0,rtsp_user="admin",rtsp_pw="admin",rtsp_ip="192.168.1.1",rtsp_port="554",rtsp_channel="1",rtsp_path="",rtsp_custom="",stream_mode=0,owner=1))
    db.session.add(models.User(username="admin",email_address="chakib.mouhoubi@gmail" ,password="administrator"))
    db.session.add(models.Track(detection_confidence=0.5,tracking_confidence=0.5))
    db.create_all() 
    db.session.commit() 

