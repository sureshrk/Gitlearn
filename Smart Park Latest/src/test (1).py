# Import packages
import os
import cv2
import numpy as np
import tensorflow as tf
import sys
import datetime
import openpyxl as op
# This is needed since the notebook is stored in the object_detection folder.
sys.path.append("..")

# Import utilites and modules
from utils import label_map_util
from utils import custom_visualization_utils as vis_util
import ocr_extraction as ocr
import firebase_storage as fb_store

# Name of the directory containing the object detection module we're using
MODEL_NAME = 'inference_graph'

# Grab path to current working directory
CWD_PATH = os.getcwd()

# Path to frozen detection graph .pb file, which contains the model that is used
# for object detection.
PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME,'frozen_inference_graph.pb')

# Path to label map file
PATH_TO_LABELS = os.path.join(CWD_PATH,'training','labelmap.pbtxt')

#Saving Images when Object is detected
IMAGE_SAVE_PATH = os.path.join(CWD_PATH,'detected')
truth = False
count = 0
visit_counter = 0;
cont = True
# Number of classes the object detector can identify
NUM_CLASSES = 1

# Dictionary of Regular People

Members_list = {
    'MH46AU1589' : {'Name' : "Navin Subbu", 'Parking' : 1 },
    'MH46N4312'  : {'Name' : 'Shree Ganesha', 'Parking' : 2 },
    'MH04HF7881' : {'Name' : 'Rajiv Iyer', 'Parking' : 3 },
    'MH04FA4886' : {'Name' : 'Sumathy Thevar', 'Parking' : 4 }
    }

Entry_List= {
    }

## Load the label map.
# Label maps map indices to category names, so that when our convolution
# network predicts `5`, we know that this corresponds to `king`.
# Here we use internal utility functions, but anything that returns a
# dictionary mapping integers to appropriate string labels would be fine
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map,
                                                            max_num_classes=NUM_CLASSES, 
                                                            use_display_name=True)

category_index = label_map_util.create_category_index(categories)

# Load the Tensorflow model into memory.
detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

    sess = tf.Session(graph=detection_graph)

# Define input and output tensors (i.e. data) for the object detection classifier
# Input tensor is the image
image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

# Output tensors are the detection boxes, scores, and classes
# Each box represents a part of the image where a particular object was detected
detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

# Each score represents level of confidence for each of the objects.
# The score is shown on the result image, together with the class label.
detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')

# Number of objects detected
num_detections = detection_graph.get_tensor_by_name('num_detections:0')

# Initialize webcam feed
video = cv2.VideoCapture(0)
ret = video.set(4,1280)
ret = video.set(3,720)

while(True):

    # Acquire frame and expand frame dimensions to have shape: [1, None, None, 3]
    # i.e. a single-column array, where each item in the column has the pixel RGB value
    ret, frame = video.read()
    # cv2.imshow("Test_Video", frame)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_expanded = np.expand_dims(frame_rgb, axis=0)

    # Perform the actual detection by running the model with the image as input
    (boxes, scores, classes, num) = sess.run(
        [detection_boxes, detection_scores, detection_classes, num_detections],
        feed_dict={image_tensor: frame_expanded})
        
    # Draw the results of the detection (aka 'visulaize the results')
    capture,frame,confidence,cropped= vis_util.visualize_boxes_and_labels_on_image_array(
        frame,
        np.squeeze(boxes),
        np.squeeze(classes).astype(np.int32),
        np.squeeze(scores),
        category_index,
        use_normalized_coordinates=True,
        line_thickness=8,
        min_score_thresh=0.60)
    
    # Here we check if the reuired Confidence value and if it is satisfied 
    # Image is Captured with Time and OCR is processed, followed by data storage in
    # Google Firebase
    if confidence > 90 :
        print(confidence)
        count = count + 1
        print (count)
        if count == 5 :        
            # Time of Detection
            time = datetime.datetime.now()
            print ("Current date and time : ")
            current_time = time.strftime("%d-%m-%y_%I:%M %p")
            time_image = time.strftime("%d%b_%I-%M%p")
            
            print(current_time)
            local_image_path = time.strftime("%B")
            local_image_name = "CAP_{}.png".format(time_image)
            img_name = "{0}/{1}/CAP_{2}.png".format(IMAGE_SAVE_PATH,local_image_path,time_image)
            cv2.imwrite(img_name, capture)
            # cv2.imwrite('Cropped',cropped)
            print("{} written!".format(img_name))
            
            # Storing in Firebase
            day = time.strftime("%d")
            time_hours = time.strftime("%I:%M:%S%p")
            text = ocr.static_image_ocr(capture,truth,cropped,cont)
            print(text)
            record = Members_list.get(text) 
            
            direction = Entry_List.get(text)
            if direction == None :
                Entry_List[text] = {'Entry' : time_hours }
                entry_time = time_hours
                exit_time = '-'
                visit_counter =visit_counter + 1
            else :
                last_time = Entry_List.pop(text)
                entry_time = last_time.get('Entry')
                exit_time = time_hours
            
            if visit_counter > 3 :
                print('No more Parking Space Available for Visitors')
            
            
            print(record)
            if record ==  None :
                print('Visitor')
                resident = 'Visitor'
                name = 'Visitor{}'.format(visit_counter)
                Dict={
                    # 'Name' : 'Visitor',
                  'License_plate' : text,
                   'Time': time_hours, 
                    'Parking_lot_No': '9',
                    'Entry' : entry_time,
                    'Exit' : exit_time
                    
                }
                
                
                fb_store.firebase_realtime_db(Dict,local_image_path,resident,name)
                fb_store.firebase_store(local_image_path,local_image_name)
            else :
                resident = "Resident"
                name = record.get('Name')
                # print(name)
                lot_number = record.get('Parking')
                print(lot_number) 
                Dict={
                    # 'Name' : name,
                  'License_plate' : text,
                   'Time': time_hours,
                    'Parking_lot_No' : lot_number,
                    'Entry' : entry_time,
                    'Exit' : exit_time
                }
                

                
                fb_store.firebase_realtime_db(Dict,local_image_path,resident,name)
                fb_store.firebase_store(local_image_path,local_image_name)
    else:
        print('No')
        count = 0
        print(count)
        
    cv2.imshow('Object detector', frame)
    
    if cv2.waitKey(1) == ord('q'):
        break

# Clean up
video.release()
cv2.destroyAllWindows()




