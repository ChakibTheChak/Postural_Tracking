from flask_wtf import FlaskForm
from wtforms import  StringField,PasswordField,SubmitField,IntegerField,BooleanField,SelectField,DateField
from wtforms.validators import Length ,EqualTo ,Email, DataRequired, ValidationError,IPAddress,URL, InputRequired
from Tracker.models import User

class RegisterForm(FlaskForm):
    # name validation function with the field to check in order to permit flaskform to call the validation function 
    def validate_username(self,username_check):
        user=User.query.filter_by(username=username_check.data).first()
        if user:
            raise ValidationError ('Username already exists ! Please try a different username')

    def validate_email_address(self, email_address_check):
        email_address=User.query.filter_by(email_address=email_address_check.data).first()
        if email_address:
            raise ValidationError ('email address already exists ! Please try a different email address')

    username=StringField(label='User Name ', validators=[Length(min=2 ,max=30),DataRequired() ])
    email_address=StringField( label='Email Address', validators=[Email(),DataRequired()])
    password1=PasswordField(label='Password ', validators=[Length(min=6),DataRequired()])
    password2=PasswordField(label='Confirm Password', validators=[EqualTo('password1'),DataRequired()])
    submit=SubmitField(label='Create Account') 


class loginForm(FlaskForm):
    # name validation function with the field to check in order to permit flaskform to call the validation function
    username=StringField(label='User Name ', validators=[DataRequired()])    
    password=PasswordField(label='Password ', validators=[DataRequired()])    
    submit=SubmitField(label='Sign in')

class SettingsForm(FlaskForm):
    # name validation function with the field to check in order to permit flaskform to call the validation function
    capture=IntegerField(label='web cam capture channel ')    
    rtsp_user=StringField(label='real time stream protocol user', validators=[DataRequired()])
    rtsp_pw=StringField(label='real time stream protocol password', validators=[DataRequired()])
    rtsp_ip=StringField(label='real time stream protocol Ip Address', validators=[IPAddress(),DataRequired()])
    rtsp_port=IntegerField(label='real time stream protocol port number', validators=[DataRequired()])
    rtsp_channel=IntegerField(label='real time stream protocol channel number', validators=[InputRequired()])
    rtsp_path=StringField(label='real time stream protocol Ip Camera Path', validators=[DataRequired()])
    rtsp_custom=StringField(label='Custom rtsp Ip Camera Path', validators=[DataRequired()])
    stream_mode=SelectField('Streaming Mode',[DataRequired()],choices=[(0,'Web Cam'),(1,'IP CAM with constructed rtsp'),(2,'IP CAM with custom rtsp')])
    submit=SubmitField(label='Save Settings') 

class PatientForm(FlaskForm):
    # name validation function with the field to check in order to permit flaskform to call the validation function
    first_name=StringField(label='First Name ', validators=[DataRequired()])
    last_name=StringField(label='Last Name ', validators=[DataRequired()])
    birth_date=DateField(label='Birth Date in format YYYY-MM-DD ', validators=[DataRequired()])
    email_address=StringField(label='Email Address ', validators=[Email(),DataRequired()])      
    pathology=StringField(label='Pathology ', validators=[DataRequired()])    
    submit=SubmitField(label='Save Patient')

class EditPatient(FlaskForm):
    submit=SubmitField(label='Edit Patient')
    
class DeletePatient(FlaskForm):
    submit=SubmitField(label='Delete Patient')
