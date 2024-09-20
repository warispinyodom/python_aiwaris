import cv2
import tkinter as tk  
from tkinter import Label, Entry, Button, Frame
from PIL import Image, ImageTk
import mysql.connector
import face_recognition
from ultralytics import YOLO

# Create main window
app = tk.Tk()
app.title("Face Registration")
app.geometry("850x700")  # Adjusted size to fit new fields
app.configure(bg='#f4f4f4')

model = YOLO('yolov8n.pt')
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Cannot open camera")
    exit()

def detect_person():
    global frame_rgb, face_locations
    check, frame = cap.read()
    if check:
        results = model(frame, conf=0.7)
        for result in results:
            for box in result.boxes:
                if box.cls == 0:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        small_frame = cv2.resize(frame, (0, 0), fx=1 / 4, fy=1 / 4)
        frame_rgb = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(frame_rgb)
        
        img = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        label_video.imgtk = imgtk
        label_video.config(image=imgtk)
    
    app.after(10, detect_person)

def save_image_to_data():
    global face_locations, frame_rgb
    student_id = input_id.get().strip()
    username = input_user.get().strip()
    group = input_group.get().strip()
    level = input_level.get().strip()
    
    if len(student_id) == 0 or len(username) == 0 or len(group) == 0 or len(level) == 0:
        print("Please enter all fields.")
        return
    
    if len(face_locations) > 0:
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="python_ai_waris"
            )
            cursor = conn.cursor()

            sql1 = "INSERT INTO users (student_id, username, `group`, `level`, status) values (%s, %s, %s, %s, 'active')"
            cursor.execute(sql1, (student_id, username, group, level))
            user_id = cursor.lastrowid  # Get the newly inserted user's ID
            conn.commit()

            face_encodings = face_recognition.face_encodings(frame_rgb, face_locations)
            if len(face_encodings) > 0:
                face_data = face_encodings[0].tobytes()

                sql2 = "UPDATE users SET picture=%s WHERE id=%s"
                cursor.execute(sql2, (face_data, user_id))
                conn.commit()

                print(f"Face data for {username} saved successfully")

                # Release camera and close application after saving data
                cap.release()
                app.destroy()
        
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        
        finally:
            cursor.close()
            conn.close()
    else:
        print("No face detected")

# Video frame
frame_video = Frame(app, bg='#ffffff', bd=2, relief='groove')
frame_video.pack(pady=20)

label_video = tk.Label(frame_video, bg='#ffffff')
label_video.pack()

# User info frame
frame_top = Frame(app, bg='#ffffff', padx=20, pady=20, bd=2, relief='groove')
frame_top.pack(pady=20)

text_id = Label(frame_top, text="รหัสนักเรียนนักศึกษา :", font=("Helvetica", 16, "bold"), bg='#ffffff')
text_id.grid(row=0, column=0, padx=10, pady=10, sticky="e")

input_id = Entry(frame_top, font=("Helvetica", 16), width=30, borderwidth=2, relief="flat")
input_id.grid(row=0, column=1, padx=10, pady=10)

text_user = Label(frame_top, text="ชื่อ - นามสกุล :", font=("Helvetica", 16, "bold"), bg='#ffffff')
text_user.grid(row=1, column=0, padx=10, pady=10, sticky="e")

input_user = Entry(frame_top, font=("Helvetica", 16), width=30, borderwidth=2, relief="flat")
input_user.grid(row=1, column=1, padx=10, pady=10)

text_group = Label(frame_top, text="กลุ่ม :", font=("Helvetica", 16, "bold"), bg='#ffffff')
text_group.grid(row=2, column=0, padx=10, pady=10, sticky="e")

input_group = Entry(frame_top, font=("Helvetica", 16), width=30, borderwidth=2, relief="flat")
input_group.grid(row=2, column=1, padx=10, pady=10)

text_level = Label(frame_top, text="ชั้น :", font=("Helvetica", 16, "bold"), bg='#ffffff')
text_level.grid(row=3, column=0, padx=10, pady=10, sticky="e")

input_level = Entry(frame_top, font=("Helvetica", 16), width=30, borderwidth=2, relief="flat")
input_level.grid(row=3, column=1, padx=10, pady=10)

# Register button
btnsubmit = Button(text="ลงทะเบียน", font=("Helvetica", 16, "bold"), command=save_image_to_data, bg='#4CAF50', fg='#ffffff', relief="raised", padx=20, pady=10)
btnsubmit.pack()

# Start face detection
detect_person()

# Start GUI
app.mainloop()

# Release camera when closing the application
cap.release()
