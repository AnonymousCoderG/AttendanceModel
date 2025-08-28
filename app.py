from flask import Flask, render_template, Response
import cv2
import face_recognition
import os
import csv
from datetime import datetime
import numpy as np
from collections import defaultdict, deque
import threading

# ===================================================================
#                          CONFIGURATION
# ===================================================================
IMAGES_PATH = "images"
TOLERANCE = 0.50
CONFIRMATION_THRESHOLD = 4
HISTORY_LENGTH = 5
# ===================================================================

# --- INITIALIZE FLASK APP ---
app = Flask(__name__)

# --- GLOBAL VARIABLES (Initialized once at startup) ---
known_face_encodings = []
known_face_names = []
video_capture = cv2.VideoCapture(0)
present_students = []

# Thread-safe lock for file writing and accessing shared variables
data_lock = threading.Lock()

# --- SETUP: LOAD FACES (Done only once) ---
def load_known_faces():
    """Loads face encodings and names from the images folder."""
    global known_face_encodings, known_face_names
    print("Loading known faces...")
    for filename in os.listdir(IMAGES_PATH):
        if filename.endswith((".jpg", ".png", ".jpeg")):
            image_path = os.path.join(IMAGES_PATH, filename)
            name = filename.split('_')[0]
            try:
                student_image = face_recognition.load_image_file(image_path)
                encoding = face_recognition.face_encodings(student_image)[0]
                known_face_encodings.append(encoding)
                known_face_names.append(name)
            except IndexError:
                print(f"Warning: No face found in {filename}. Please replace this image.")
    if not known_face_encodings:
        print("FATAL: No known faces loaded. Check the 'images' folder. Exiting.")
        exit()
    print(f"Known faces loaded successfully for {len(set(known_face_names))} unique people.")

def generate_frames():
    """Generator function to yield processed video frames."""
    # Local variables for frame processing
    process_this_frame = True
    face_recognition_history = defaultdict(lambda: deque(maxlen=HISTORY_LENGTH))

    while True:
        success, frame = video_capture.read()
        if not success:
            print("Error: Could not read frame from webcam.")
            break

        # Alternate frame processing for performance
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
            for i, name in enumerate(current_face_names):
                face_recognition_history[i].append(name)
                if len(face_recognition_history[i]) == HISTORY_LENGTH:
                    most_common_name = max(set(face_recognition_history[i]), key=list(face_recognition_history[i]).count)
                    if list(face_recognition_history[i]).count(most_common_name) >= CONFIRMATION_THRESHOLD:
                        stable_name = most_common_name
                        stable_face_names.append(stable_name)

                        # --- Thread-safe Attendance Marking ---
                        with data_lock:
                            if stable_name != "Unknown" and stable_name not in present_students:
                                current_time = datetime.now().strftime("%H:%M:%S")
                                current_date = datetime.now().strftime("%Y-%m-%d")
                                attendance_file = f"attendance_{current_date}.csv"
                                
                                # Open file within the lock
                                with open(attendance_file, 'a+', newline='') as f:
                                    # Move cursor to the start to check if file is empty
                                    f.seek(0)
                                    if not f.read(1): # Check if file is empty
                                        csv.writer(f).writerow(["Name", "Time"])
                                    csv.writer(f).writerow([stable_name, current_time])
                                
                                present_students.append(stable_name)
                                print(f"STABLE ID: Attendance marked for {stable_name} at {current_time}")
                    else:
                        stable_face_names.append("Processing...")
                else:
                    stable_face_names.append("Processing...")

        process_this_frame = not process_this_frame

        # --- Draw results on the frame ---
        for (top, right, bottom, left), name in zip(face_locations, stable_face_names):
            top *= 4; right *= 4; bottom *= 4; left *= 4
            box_color = (0, 0, 255) if name in ["Unknown", "Processing..."] else (0, 255, 0)
            cv2.rectangle(frame, (left, top), (right, bottom), box_color, 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), box_color, cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        # Encode the frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # Yield the frame in the correct format for streaming
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# --- FLASK ROUTES ---
@app.route('/')
def index():
    """Renders the main web page."""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Route for the video streaming."""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# --- MAIN EXECUTION ---
if __name__ == '__main__':
    load_known_faces()
    # The 'threaded=True' is important to handle background processing
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)