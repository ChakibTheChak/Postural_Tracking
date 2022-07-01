from Tracker import app, render_template,Response, request ,db ,redirect,url_for, flash,get_flashed_messages ,login_user,logout_user, login_required, current_user,session
from Tracker import functions ,forms , IntegrityError
from Tracker.models import User , Settings, Patient , Track


## Global variables ###############################################################################################################################################
global tracking,btn_start,btn_stop
tracking=0

## Routes ###############################################################################################################################################

## Home Route ###############################################################################################################################################
@app.route('/')
@app.route('/home')
def home_page():
    return render_template('/home.html')

## Shutdown Route ###############################################################################################################################################
@app.route('/shutdown', methods=['GET'])
def shutdown():
    functions.shutdown_server()
    return 'Server shutting down...'
## Register Route ###############################################################################################################################################
@app.route('/register', methods=['GET','POST'])
def register_page():
    form =forms.RegisterForm()
    if form.validate_on_submit():
        user_to_create=User(username=form.username.data ,email_address=form.email_address.data ,password=form.password1.data)        
        db.session.add(user_to_create)
        db.session.commit()
        
        settings_to_create=Settings(capture=0,rtsp_user="admin",rtsp_pw="admin",rtsp_ip="192.168.1.1",rtsp_port="554",rtsp_channel="1",rtsp_path="",rtsp_custom="",stream_mode=0,owner=user_to_create.id)
        db.session.add(settings_to_create)
        db.session.commit()

        return redirect(url_for('home_page'))

    if form.errors != {}:
       for err_msg in form.errors.values():
           flash(f' there was an error: {err_msg}',category='danger')
    return  render_template('register.html', form=form)
## Patient Register Route ###############################################################################################################################################
@app.route('/patient', methods=['GET','POST'])
@login_required
def patient_register_page():
    form =forms.PatientForm()
    if form.validate_on_submit():
        patient_to_create=Patient(first_name=form.first_name.data ,last_name=form.last_name.data,birthdate=form.birth_date.data,
        email_address=form.email_address.data ,pathology=form.pathology.data,owner=current_user.id)
        try:
            db.session.add(patient_to_create)
            db.session.commit()
            flash(f' the new patient has been registred',category='success')
        except IntegrityError as e :
            db.session.rollback()
            flash(f' there was a duplicated information :{e.orig.args} ',category='danger')
        return redirect(url_for('patient_register_page'))

    if form.errors != {}:
       for err_msg in form.errors.values():
           flash(f' there was an error: {err_msg}',category='danger')
    return  render_template('patient_form.html', form=form)

## Patient list Route ###############################################################################################################################################
@app.route('/patient_list', methods=['GET','POST'])
@login_required
def patient_page():
    EditPatient=forms.EditPatient(request.form)
    DeletePatient=forms.DeletePatient(request.form)
    Patient_Form=forms.PatientForm(request.form)
    patients_list=Patient.query.filter_by(owner=current_user.id).all()
 
    if EditPatient.validate_on_submit():
        id_edit=request.form.get("Edit")
        print("Patient ID is :",id_edit) 
        patient_to_edit=Patient.query.filter_by(id=id_edit).first()
        patient_to_edit.first_name=Patient_Form.first_name.data
        patient_to_edit.last_name=Patient_Form.last_name.data
        patient_to_edit.birth_date=Patient_Form.birth_date.data
        patient_to_edit.email_address=Patient_Form.email_address.data
        patient_to_edit.pathology=Patient_Form.pathology.data        
        try:
            db.session.commit()
            flash(f'Success : Patient modified with sucess', category='success')
            updated_patient=Patient.query.filter_by(id=id_edit).first()                        
        except IntegrityError as e :
            flash(f'Issue updating patient in database :{e.orig.args}' , category='danger')            
        return  render_template('patient.html', patients=patients_list, patient_form=Patient_Form,EditPatient=EditPatient,DeletePatient=DeletePatient)
    else :
        print(" I am here waiting for request other than POST")

    return  render_template('patient.html', patients=patients_list, patient_form=Patient_Form,EditPatient=EditPatient,DeletePatient=DeletePatient)
## Login Route ###############################################################################################################################################
@app.route('/login', methods=['GET','POST'])
def login_page():
    form =forms.loginForm()
    if form.validate_on_submit():
        attempted_user=User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'Success : you are logged in as :{attempted_user.username}', category='success')
            # manage the session in order to close session when the browser is closed 
            # a login is required once reopened
            session.permanent=False
            session.modified=True

            return redirect(url_for('home_page'))
        else:
            flash(f'username and password are not match ! please try again!', category='danger')      
 
    return  render_template('login.html', form=form)
## Logout Route ###############################################################################################################################################
@app.route('/logout', methods=['GET','POST'])
def logout_page():
    logout_user()
    flash(f'You have been logged out !', category='info')
    return redirect(url_for("home_page"))
## Settings Route ###############################################################################################################################################
@app.route('/Settings',methods=['GET','POST'])
@login_required
def settings_page():
    form=forms.SettingsForm(request.form)
    print (current_user)
    print (current_user.id)
    settings=Settings.query.filter_by(owner=current_user.id).first() 
    if request.method=='POST':
        if form.validate_on_submit():            
            settings.capture=form.capture.data
            settings.rtsp_user=form.rtsp_user.data
            settings.rtsp_pw=form.rtsp_pw.data
            settings.rtsp_ip=form.rtsp_ip.data
            settings.rtsp_port=form.rtsp_port.data
            settings.rtsp_channel=form.rtsp_channel.data
            settings.rtsp_path=form.rtsp_path.data
            settings.rtsp_custom=form.rtsp_custom.data
            settings.stream_mode=form.stream_mode.data
            try:              
                db.session.commit()
                updated_settings=Settings.query.filter_by(owner=current_user.id).first()
                flash(f'Success : Parameters Saved', category='success')
                #print( 'sucess db updated')
                return render_template('Settings.html',form=form,settings=updated_settings)
            except :
                flash(f'Issue updating settings in database', category='danger')
                #print (' issue with update')
                return render_template('Settings.html',form=form,settings=settings)            
        else :
            if form.errors !={}:
                for err_msg in form.errors.items():
                    #print(' got error message with the validation form ')
                    flash(f'parameter is not valid ! please try again :{err_msg}', category='danger')
    else :
        #print( 'we ve got get request')        
        form.capture.data=settings.capture       
        form.rtsp_pw.data=settings.rtsp_pw
        form.rtsp_ip.data=settings.rtsp_ip
        form.rtsp_port.data=settings.rtsp_port
        form.rtsp_channel.data=settings.rtsp_channel
        form.rtsp_path.data=settings.rtsp_path
        form.rtsp_custom.data=settings.rtsp_custom
        form.stream_mode.data=settings.stream_mode        
    return render_template('Settings.html',form=form, settings=settings)
## Video Route ############################################################################################################################################### 
@app.route('/video')
def video():
    global tracking
    user_settings=Settings.query.filter_by(owner=current_user.id).first()
    capture=user_settings.capture 
    stream_mode=user_settings.stream_mode
    rtsp_path=user_settings.rtsp_path
    custom_rtsp_path=user_settings.rtsp_custom 
    tracking=0    
    return Response(functions.gen_frames(capture,stream_mode,rtsp_path,custom_rtsp_path,tracking), mimetype='multipart/x-mixed-replace; boundary=frame')
## Streaming Route ###############################################################################################################################################
@app.route('/Streaming')
@login_required
def stream_page():
   global tracking
   hight=str(100)+"%" 
   width=str(100)+"%"
   patients=Patient.query.filter_by(owner=current_user.id).all()
   form =forms.TrackForm(request.form)
   track=Track.query.filter_by(owner=current_user.id).all()
   print (patients)
   tracking=0
   return render_template('Video_Stream.html',hight=hight,width=width,patients=patients, btn_status='Start Tracking',form=form,track=track)
## Tracking Route ###############################################################################################################################################
@app.route('/tracking',methods=['POST','GET'])
def track_page():
    global tracking
    tracking=0
    patients=Patient.query.filter_by(owner=current_user.id).all()
    form =forms.TrackForm(request.form)
    track=Track.query.filter_by(owner=current_user.id).all()
    hight=str(100)+"%" 
    width=str(100)+"%"      
    if request.method=='POST':
        if request.form.get('tracking')=='Start Tracking' :            
            tracking= not tracking                                          
            return render_template('Video_Stream.html', btn_status='Stop Tracking',hight=hight,width=width,patients=patients,form=form, track=track)
        else :
            tracking= not tracking            
            return render_template('Video_Stream.html', btn_status='Start Tracking',hight=hight,width=width,patients=patients,form=form, track=track)      
    elif request.method=="GET":
        return render_template('Video_Stream.html',btn_status='Start Tracking',hight=hight,width=width,patients=patients,form=form, track=track)
## Tracking Seetings  Route ###############################################################################################################################################
@app.route('/track', methods=['GET','POST'])
@login_required
def tracking_settings_page():
    form =forms.TrackForm(request.form)
    track_settings=Track.query.filter_by(owner=current_user.id).first()
    if request.method=='POST': 
        if form.validate_on_submit():
            track_settings.tracking_confidence=form.tracking_confidence.data
            track_settings.detection_confidence=form.detection_confidence.data 
            track_settings.width=form.width.data
            track_settings.height=form.height.data     
            try:           
                db.session.commit()
                updated_track_settings=Settings.query.filter_by(owner=current_user.id).first()
                flash(f' the new patient has been registred',category='success')
                return  render_template('track_form.html', form=form ,track=updated_track_settings)
            except IntegrityError as e :
                db.session.rollback()
                flash(f' there was a duplicated information :{e.orig.args} ',category='danger')
                return  render_template('track_form.html', form=form ,track=track_settings)
        if form.errors != {}:
            for err_msg in form.errors.values():
                flash(f' there was an error: {err_msg}',category='danger')
        
    else :
        form.tracking_confidence.data=track_settings.tracking_confidence
        form.detection_confidence.data=track_settings.detection_confidence
        form.width.data=track_settings.width
        form.height.data=track_settings.height

    return  render_template('track_form.html', form=form , track=track_settings)