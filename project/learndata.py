import cv2
from ultralytics import YOLO
import face_recognition
import mysql.connector
import numpy as np
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont  # Import from PIL

# YOLO model for object detection
model = YOLO('yolov8n.pt')  # pretrained YOLOv8n model

# Database connection for face recognition and logging passes
try:
    conn = mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="",
        database="python_ai_waris"
    )
    cursor = conn.cursor(dictionary=True)
except mysql.connector.Error as err:
    print(f"Error: {err}")
    exit()

# Load all faces from the database
cursor.execute('''
SELECT username, picture 
FROM users 
    ''')
faces = cursor.fetchall()

if len(faces) == 0:
    print("No faces found in the database.")
    conn.close()
    exit()

# Convert face data to numpy arrays
all_faces = [np.frombuffer(face["picture"], dtype=np.float64) for face in faces]
print("Loaded all faces.")

# Load a Thai font (ensure you have the font file)
font_path = "C:/NodeAPI/project/THSarabunNew/THSarabunNew.ttf"  # Replace with the path to a Thai font file
thai_font = ImageFont.truetype(font_path, 32)  # Load Thai font with desired size

def draw_text_pil(image, text, position, font, color=(0, 0, 255)):
    """Draw text using PIL."""
    pil_image = Image.fromarray(image)
    draw = ImageDraw.Draw(pil_image)
    draw.text(position, text, font=font, fill=color)
    return np.array(pil_image)

def log_pass(name, direction, frame):
    """Log the person passing with their name and direction (in/out) into the database and save a picture."""
    timestamp = datetime.now()
    
    # Define the filename path for the image
    filename = f"{name}_{direction}_{timestamp.strftime('%Y%m%d_%H%M%S')}.jpg"
    filepath = os.path.join('C:/NodeAPI/app/public/images', filename)
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Save the frame with a unique filename
    cv2.imwrite(filepath, frame)
    
    # Store relative path in the database
    relative_path = f'images/{filename}'
    try:
        cursor.execute('''
        INSERT INTO passes (name, timestamp, direction, image_path)
        VALUES (%s, %s, %s, %s)
        ''', (name, timestamp, direction, relative_path))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    
    print(f"Logged: {name} crossed {direction} at {timestamp} and image saved as {filepath}")

# Video capture
cap = cv2.VideoCapture(1)
if not cap.isOpened():
    print("Error: Could not open video capture.")
    conn.close()
    exit()

count_in = 0
count_out = 0
track = {}
face_logged = {}  # Dictionary to track whether a face has been logged
cx = None  # Variable to store center line x-coordinate

while True:
    ok, frame = cap.read()
    if not ok:
        print("Failed to capture image from webcam.")
        break

    h, w, _ = frame.shape
    if cx is None:
        cx = int(w / 2)  # Initialize center line coordinate

    # YOLO object detection
    results = model.track(frame, conf=0.5, verbose=False, classes=[0], persist=True)
    if not results:
        print("No objects detected.")
        continue

    # Draw center line and count display
    img = results[0].plot()  # Use img to show results but do not draw YOLO boxes
    cv2.line(img, (cx, 0), (cx, h), (29, 227, 185), 1)
    cv2.putText(img, f"IN={count_in} OUT={count_out}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 131), 1, cv2.LINE_AA)
    
    # Resize the frame for face recognition (1/4 of original size)
    small_frame = cv2.resize(frame, (frame.shape[1] // 4, frame.shape[0] // 4))
    
    # Convert the resized frame to RGB
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    
    # Detect face locations and encode faces
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
    
    print(f"Found {len(face_locations)} face(s)")

    # Draw bounding boxes for detected faces
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Scale back up face locations to match the frame size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4
        
        # Draw a rectangle around the face
        cv2.rectangle(img, (left, top), (right, bottom), (0, 255, 27 ), 1)
        
        # Perform face recognition
        name = "Unknown"  # Default name
        face_distances = face_recognition.face_distance(all_faces, face_encoding)
        
        print("Face distances:", face_distances)  # Debugging
        if len(face_distances) > 0:
            min_index = np.argmin(face_distances)
            min_distance = face_distances[min_index]
            threshold = 0.5  # Adjusted threshold
            
            if min_distance < threshold:
                name = faces[min_index]["username"]
                accuracy = (1 - min_distance) * 100  # Calculate accuracy percentage
                print(f"Face recognized: {name} with distance {min_distance} ({accuracy:.2f}%)")

                # Log recognized face crossing the line if applicable
                if name not in face_logged:
                    face_logged[name] = True

            # Draw Thai name with PIL (support for Thai characters)
            img = draw_text_pil(img, name, (left, top - 40), thai_font, (0, 0, 255))

    # Loop through all detected objects
    for result in results:
        boxes = result.boxes
        for idx in range(len(result.boxes.cls)):
            classId = int(result.boxes.cls[idx])
            box = result.boxes.xyxy[idx]
            trackId = str(int(result.boxes.id[idx])) if result.boxes.id is not None else None

            if trackId is None:
                continue

            # Update tracking information
            if trackId not in track:
                track[trackId] = {"left": int(box[0]), "right": int(box[2])}
            else:
                x_cur_left = int(box[0])
                x_cur_right = int(box[2])
                x_prev = track[trackId]
                track[trackId] = {"left": x_cur_left, "right": x_cur_right}

                # Count objects crossing the center line
                if x_prev["left"] < cx and x_cur_left >= cx:
                    count_in += 1
                    log_pass(name, "in", frame)  # Use recognized name and current frame
                elif x_prev["right"] > cx and x_cur_right <= cx:
                    count_out += 1
                    log_pass(name, "out", frame)  # Use recognized name and current frame

    # Show the image
    cv2.imshow('detect', img)
    
    # Wait for key press
    key = cv2.waitKey(1) & 0xFF
    if key == ord('r'):  # Press 'r' to register
        cap.release()
        cv2.destroyAllWindows()
        conn.close()
        os.system('python project/learnregis.py')
        exit()
    elif key == 27:  # ESC key to exit
        break
    elif cv2.getWindowProperty('detect', cv2.WND_PROP_VISIBLE) < 1:  # Check if window is closed
        break

cap.release()
cv2.destroyAllWindows()
conn.close()
