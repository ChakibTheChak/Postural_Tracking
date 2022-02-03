from sqlalchemy import UniqueConstraint
from Tracker import  db ,app,bcrypt,login_manager ,datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
  
class User(db.Model, UserMixin):
    id =db.Column(db.Integer(),primary_key=True)
    username=db.Column(db.String(length=30), nullable=False,unique=True)
    email_address=db.Column(db.String(length=50),nullable=False,unique=True)
    password_hash=db.Column(db.String(length=128),nullable=False)
    settings=db.relationship('Settings',backref='owned_user',lazy=True)
    patient=db.relationship('Patient',backref='owned_user',lazy=True)

    @property 
    def password(self):
        return self.password
    
    @password.setter
    def password(self,plain_text_password):
        self.password_hash=bcrypt.generate_password_hash(plain_text_password).decode('utf-8')
    
    def check_password_correction(self,attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)
        

class Profile(db.Model):
    id =db.Column(db.Integer(),primary_key=True)
    first_name=db.Column(db.String(length=30), nullable=False)
    name=db.Column(db.String(length=30), nullable=False)
    birth_date=db.Column(db.Date(), nullable=False)
    pathology=db.Column(db.String(length=45), nullable=False)
     
    # Magic methode to return first name insteade of  incremental id
    def __repr__(self):
        return f'Profile{self.first_name}'

class Settings(db.Model):
    id =db.Column(db.Integer(),primary_key=True)
    capture=db.Column(db.Integer(), nullable=False)
    rtsp_user=db.Column(db.String(length=45), nullable=False)
    rtsp_pw=db.Column(db.String(length=45), nullable=False)
    rtsp_ip=db.Column(db.String(length=16), nullable=False)
    rtsp_port=db.Column(db.String(length=254), nullable=False)
    rtsp_channel=db.Column(db.String(length=254), nullable=False)
    rtsp_path=db.Column(db.String(length=254), nullable=False)
    rtsp_custom=db.Column(db.String(length=1024), nullable=False)
    stream_mode=db.Column(db.Integer(), nullable=False)  #0 capture web cam , 1 Ip camera with standard rtsp path , 2 custom rtsp path
    owner=db.Column(db.Integer() ,db.ForeignKey('user.id'))

class Track(db.Model):
    id =db.Column(db.Integer(),primary_key=True)
    detection_confidence=db.Column(db.Float(), nullable=False)
    tracking_confidence=db.Column(db.Float(), nullable=False)

class Patient(db.Model):
    id =db.Column(db.Integer(),primary_key=True)
    first_name=db.Column(db.String(length=30), nullable=False,unique=True)
    last_name=db.Column(db.String(length=30), nullable=False,unique=False)
    birthdate=db.Column(db.Text(),nullable=False,unique=False)  # TEXT as ISO8601 strings ("YYYY-MM-DD HH:MM:SS.SSS").
    email_address=db.Column(db.String(length=50),nullable=False,unique=True)
    pathology=db.Column(db.String(length=50),nullable=False,unique=False)
    creation_date=db.Column(db.DateTime ,default=datetime.datetime.utcnow)
    owner=db.Column(db.Integer() ,db.ForeignKey('user.id'))
    UniqueConstraint('first_name','last_name')
         
    # Magic methode to return first name insteade of  incremental id
    def __repr__(self):
        return f'Patient{self.first_name}'


