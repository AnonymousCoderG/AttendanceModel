import cv2
import face_recognition
import os
import csv
from datetime import datetime
import numpy as np

# ===================================================================
#                          CONFIGURATION
# ===================================================================
# --- 1. Path to the image dataset ---
IMAGES_PATH = "images"

# --- 2. Recognition Tolerance (Lower is Stricter) ---
# A value of 0.55 is a good starting point. If you still get false
# matches, try lowering it to 0.5. If known people are marked
# "Unknown", you might need to raise it slightly to 0.6.
TOLERANCE = 0.55
# ===================================================================


# --- SETUP ---

# Lists to store known face encodings and their corresponding names
known_face_encodings = []
known_face_names = []

# Load student images and learn how to recognize them
print("Loading known faces...")
for filename in os.listdir(IMAGES_PATH):
    if filename.endswith((".jpg", ".png", ".jpeg")):
        image_path = os.path.join(IMAGES_PATH, filename)
        
        # The name is extracted from the filename (e.g., "Gouri_1.jpg" -> "Gouri")
        name = filename.split('_')[0]
        
        student_image = face_recognition.load_image_file(image_path)
        
        try:
            student_face_encoding = face_recognition.face_encodings(student_image)[0]
            known_face_encodings.append(student_face_encoding)
            known_face_names.append(name)
        except IndexError:
            print(f"Warning: No face found in {filename}. Skipping this file.")

print(f"Known faces loaded successfully. Found images for {len(set(known_face_names))} unique people.")

# Get a reference to the webcam
video_capture = cv2.VideoCapture(0)

# Prepare for attendance logging
current_date = datetime.now().strftime("%Y-%m-%d")
attendance_file = f"attendance_{current_date}.csv"

# --- INITIALIZE VARIABLES FOR THE LOOP ---
present_students = []
face_locations = []
face_names = []
process_this_frame = True

# Open the attendance file and prepare to write
with open(attendance_file, 'a', newline='') as f:
    writer = csv.writer(f)
    if os.stat(attendance_file).st_size == 0:
        writer.writerow(["Name", "Time"])

    # --- MAIN LOOP ---
    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("Error: Could not read frame from webcam.")
            break

        # --- ALTERNATE FRAME PROCESSING ---
        if process_this_frame:
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            current_face_locations = face_recognition.face_locations(rgb_small_frame)
            current_face_encodings = face_recognition.face_encodings(rgb_small_frame, current_face_locations)

            face_names = []
            for face_encoding in current_face_encodings:
                
                # --- IMPROVED MATCHING LOGIC ---
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                name = "Unknown"

                if len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances)
                    best_match_distance = face_distances[best_match_index]

                    # If the best match is within our strict tolerance, accept it
                    if best_match_distance < TOLERANCE:
                        name = known_face_names[best_match_index]

                face_names.append(name)

                # --- Attendance Marking ---
                if name != "Unknown" and name not in present_students:
                    current_time = datetime.now().strftime("%H:%M:%S")
                    writer.writerow([name, current_time])
                    f.flush()
                    present_students.append(name)
                    print(f"Attendance marked for {name} at {current_time}")
            
            face_locations = current_face_locations

        process_this_frame = not process_this_frame

        # --- DISPLAY RESULTS (EVERY FRAME) ---
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            box_color = (0, 0, 255) if name == "Unknown" else (0, 255, 0)

            cv2.rectangle(frame, (left, top), (right, bottom), box_color, 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), box_color, cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        cv2.imshow('Attendance System', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# --- CLEANUP ---
video_capture.release()
cv2.destroyAllWindows()
print("Attendance marking session finished.")