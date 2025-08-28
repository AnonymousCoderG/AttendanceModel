import cv2
import face_recognition
import os
import csv
from datetime import datetime
import numpy as np
from collections import defaultdict, deque

# ===================================================================
#                          CONFIGURATION
# ===================================================================
IMAGES_PATH = "images"
TOLERANCE = 0.50

# --- Confidence Buffer Settings ---
# How many of the last frames must match to be considered a stable ID
CONFIRMATION_THRESHOLD = 4
# How many recent frames to store for each face
HISTORY_LENGTH = 5
# ===================================================================

# --- SETUP ---
known_face_encodings = []
known_face_names = []

print("Loading known faces...")
# ... (Image loading logic is unchanged, but ensure your dataset is clean!) ...
for filename in os.listdir(IMAGES_PATH):
    if filename.endswith((".jpg", ".png", ".jpeg")):
        image_path = os.path.join(IMAGES_PATH, filename)
        name = filename.split('_')[0]
        student_image = face_recognition.load_image_file(image_path)
        try:
            student_face_encoding = face_recognition.face_encodings(student_image)[0]
            known_face_encodings.append(student_face_encoding)
            known_face_names.append(name)
        except IndexError:
            print(f"Warning: No face found in {filename}. Please replace this image.")
if not known_face_encodings:
    print("FATAL: No known faces were loaded. Check the 'images' folder. Exiting.")
    exit()
print(f"Known faces loaded successfully. Found images for {len(set(known_face_names))} unique people.")

video_capture = cv2.VideoCapture(0)
current_date = datetime.now().strftime("%Y-%m-%d")
attendance_file = f"attendance_{current_date}.csv"

# --- INITIALIZE VARIABLES FOR THE LOOP ---
present_students = []
process_this_frame = True

# --- ADVANCED: Variables for Confidence Buffering ---
# This dictionary will store a history of recent recognitions for each face track
# The key will be a simple track ID (0, 1, 2...)
face_recognition_history = defaultdict(lambda: deque(maxlen=HISTORY_LENGTH))
# This list will hold the final, stable names to be displayed
stable_face_names = []

with open(attendance_file, 'a', newline='') as f:
    writer = csv.writer(f)
    if os.stat(attendance_file).st_size == 0:
        writer.writerow(["Name", "Time"])

    # --- MAIN LOOP ---
    while True:
        ret, frame = video_capture.read()
        if not ret: break

        if process_this_frame:
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            face_locations = face_recognition.face_locations(rgb_small_frame)
            current_face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            current_face_names = []
            for face_encoding in current_face_encodings:
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                name = "Unknown"
                if len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances)
                    if face_distances[best_match_index] < TOLERANCE:
                        name = known_face_names[best_match_index]
                current_face_names.append(name)

            # --- CONFIDENCE BUFFER LOGIC ---
            stable_face_names = []
            # We assign a temporary track ID based on the order of detection
            for i, name in enumerate(current_face_names):
                face_recognition_history[i].append(name)
                # Check if the history is full and consistent
                if len(face_recognition_history[i]) == HISTORY_LENGTH:
                    # Count occurrences of each name in the history
                    name_counts = defaultdict(int)
                    for past_name in face_recognition_history[i]:
                        name_counts[past_name] += 1
                    
                    # Find the most common name
                    most_common_name = max(name_counts, key=name_counts.get)

                    # If the most common name meets our threshold, it's a stable ID
                    if name_counts[most_common_name] >= CONFIRMATION_THRESHOLD:
                        stable_name = most_common_name
                        stable_face_names.append(stable_name)

                        # --- Attendance Marking (moved here for stability) ---
                        if stable_name != "Unknown" and stable_name not in present_students:
                            current_time = datetime.now().strftime("%H:%M:%S")
                            writer.writerow([stable_name, current_time])
                            f.flush()
                            present_students.append(stable_name)
                            print(f"STABLE ID: Attendance marked for {stable_name} at {current_time}")
                    else:
                        # If not confident, display "Processing..."
                        stable_face_names.append("Processing...")
                else:
                    # If history isn't full yet, display "Processing..."
                    stable_face_names.append("Processing...")

        process_this_frame = not process_this_frame

        # --- DISPLAY RESULTS (EVERY FRAME) ---
        # We now use 'stable_face_names' for display
        for (top, right, bottom, left), name in zip(face_locations, stable_face_names):
            top *= 4; right *= 4; bottom *= 4; left *= 4

            box_color = (0, 0, 255) if name in ["Unknown", "Processing..."] else (0, 255, 0)

            cv2.rectangle(frame, (left, top), (right, bottom), box_color, 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), box_color, cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        cv2.imshow('Attendance System', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'): break

# --- CLEANUP ---
video_capture.release()
cv2.destroyAllWindows()
print("Attendance marking session finished.")