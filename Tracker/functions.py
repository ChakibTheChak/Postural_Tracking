from Tracker import  request ,np ,cv2 ,mp_position,mp_drawing

# Functions ###################################################################################################################

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    
def calculate_angle(a,b,c):
    a=np.array(a) #first 
    b=np.array(b) # mid 
    c=np.array(c) # End 

    radians= np.arctan2(c[1]-b[1],c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle=np.abs(radians*180.0/np.pi)
    if angle>180.0 :
        angle=380-angle
    return angle


def gen_frames(Capture,stream_mode,rtsp_path,custom_rtsp_path,tracking,min_detec_confi=0.6,min_track_confi=0.6):
    counter=0
    stage=None
    # video Capture instance ##################################################################
    if  stream_mode==0:
        cap=cv2.VideoCapture(Capture,cv2.CAP_DSHOW)  # If new version of windows no need to add cv2.CAP_DSHOW as CAP_MSMF is the neuw defalut
    elif stream_mode==1:
        cap=cv2.VideoCapture(rtsp_path)
    elif stream_mode==2:
        cap=cv2.VideoCapture(custom_rtsp_path)

    #Stream handeling ##################################################################
    with mp_position.Pose(min_detection_confidence=min_detec_confi, min_tracking_confidence=min_track_confi) as pose:                
        while cap.isOpened():
            ret,frame=cap.read()
            try:
                if not tracking:
                    ret, buffer = cv2.imencode('.jpg', cv2.flip(frame,1))
                    frame = buffer.tobytes()
                    yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                else :  
                        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                        # print("Camera resolution is:" ,width,height)

                        image=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        fliped_image=cv2.flip(image,1)                        
                        fliped_image.flags.writeable=False                        

                        #Make detection ##################################################################  
                        results=pose.process(fliped_image)
                        # print (results)

                        #recolor back to BGR##################################################################
                        fliped_image.flags.writeable=True
                        fliped_image=cv2.cvtColor(fliped_image, cv2.COLOR_RGB2BGR)

                        # extract landmarks ##################################################################
                        try:
                            landmarks=results.pose_landmarks.landmark

                            left_eye=[landmarks[mp_position.PoseLandmark.LEFT_EYE.value].x,landmarks[mp_position.PoseLandmark.LEFT_EYE.value].y]
                            right_eye=[landmarks[mp_position.PoseLandmark.RIGHT_EYE.value].x,landmarks[mp_position.PoseLandmark.RIGHT_EYE.value].y]

                            left_ear=[landmarks[mp_position.PoseLandmark.LEFT_EAR.value].x,landmarks[mp_position.PoseLandmark.LEFT_EAR.value].y]
                            right_ear=[landmarks[mp_position.PoseLandmark.RIGHT_EAR.value].x,landmarks[mp_position.PoseLandmark.RIGHT_EAR.value].y]

                            left_shoulder=[landmarks[mp_position.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_position.PoseLandmark.LEFT_SHOULDER.value].y]
                            right_shoulder=[landmarks[mp_position.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_position.PoseLandmark.RIGHT_SHOULDER.value].y]
                            nose=[landmarks[mp_position.PoseLandmark.NOSE.value].x, landmarks[mp_position.PoseLandmark.NOSE.value].y]



                            Left_HS_angle= round(calculate_angle(left_eye,left_shoulder,right_shoulder)) # left Head shoulder
                            right_HS_angle=round(calculate_angle(right_eye,right_shoulder,left_shoulder)) # right Head shoulder

                            left_ESS_angle= round(calculate_angle(left_ear,left_shoulder,right_shoulder)) # left Ear Shoulder Shoulder ( opposit)
                            right_ESS_angle=round(calculate_angle(right_ear,right_shoulder,left_shoulder)) # right Ear Shoulder Shoulder
                            center_NH_angle=round(calculate_angle(left_shoulder,nose,right_shoulder))


                            #print("left  eye shoulder angle is ",Left_HS_angle)
                            #print("right eye shoulder angle  is ",right_HS_angle)
                        
                            #print(landmarks)
                            #print( landmarks[mp_position.PoseLandmark.LEFT_EYE.value])
                            #print( landmarks[mp_position.PoseLandmark.RIGHT_EYE.value])
                            #print( landmarks[mp_position.PoseLandmark.LEFT_SHOULDER.value])
                            #print( landmarks[mp_position.PoseLandmark.RIGHT_SHOULDER.value])
                                # curl counter logic
                            if center_NH_angle<65.0:
                                stage="head Up"
                                rbg_color=(127,255,0)
                            if 70.0>center_NH_angle>65.0 :
                                stage="head centred"
                                rbg_color=(245,117,16)
                            if 90.0>center_NH_angle>70.0 and stage=="head centred" :
                                stage= "head down"
                                rbg_color=(255,127,80)
                            if center_NH_angle>90.0 and stage=="head down":
                                stage= "head too much down"
                                rbg_color=(0,0,255)
                                counter+=1
                            else :
                                rbg_color=(127,255,0) 

                            # Visualize / Render landmarks  
                            mp_drawing.draw_landmarks(fliped_image, results.pose_landmarks,mp_position.POSE_CONNECTIONS,
                            mp_drawing.DrawingSpec(color=(245,117,66),thickness=2,circle_radius=2),mp_drawing.DrawingSpec(color=(245,66,230),thickness=2,circle_radius=2))
                            
                            
                            cv2.rectangle(fliped_image,(0,0),(225,73),rbg_color,-1)
                            cv2.rectangle(fliped_image,(0,0),(225,73),rbg_color,-1)
                            # Rep Data 
                            cv2.putText(fliped_image,stage,(15,12),cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,0.5,(0,0,0),1,cv2.LINE_AA)
                            cv2.putText(fliped_image,str(counter),(10,60),cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,2,(255,255,255),1,cv2.LINE_AA)

                            org=[width,height]
                            org1=[640,480]
                            cv2.putText(fliped_image, str(left_ESS_angle)+" degrees", tuple(np.multiply(left_shoulder,org).astype(int)), cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),2 ,cv2.LINE_AA)
                            cv2.putText(fliped_image, str(right_ESS_angle)+" degrees", tuple(np.multiply(right_shoulder,org).astype(int)), cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),2 ,cv2.LINE_AA)
                            cv2.putText(fliped_image, str(center_NH_angle)+" degrees", tuple(np.multiply(nose,org).astype(int)), cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),2 ,cv2.LINE_AA)                      
                                   
                        except:
                            cv2.putText(fliped_image,"No Human Detected",(15,12),cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,0.5,(0,0,0),1,cv2.LINE_AA)                       
                        
                        ret, buffer = cv2.imencode('.jpg', fliped_image)                        
                        frame = buffer.tobytes()
                        yield (b'--frame\r\n'
                                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

            except Exception as e:
                    cap.release()
                    print("Video process Error:",e)
                    cv2.destroyAllWindows() 
                    pass
        # when cap is closed         
        cap.release()
        cv2.destroyAllWindows() 


                

