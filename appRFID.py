# from flask import Flask, Response, render_template, request, jsonify
# import cv2
# import face_recognition
# import os
# import csv
# from datetime import datetime
# import numpy as np
# import threading

# app = Flask(__name__)

# # --- 1. GLOBAL VARIABLES & SETUP ---

# # Path to the directory containing student images
# IMAGES_PATH = "images"

# # Lists to store known face encodings and names
# known_face_encodings = []
# known_face_names = []

# # --- Load student images and learn how to recognize them ---
# print("Loading known faces...")
# for filename in os.listdir(IMAGES_PATH):
#     if filename.lower().endswith((".jpg", ".png", ".jpeg")):
#         image_path = os.path.join(IMAGES_PATH, filename)
#         try:
#             student_image = face_recognition.load_image_file(image_path)
#             student_face_encoding = face_recognition.face_encodings(student_image)[0]
#             known_face_encodings.append(student_face_encoding)
#             # Use the filename (without extension) as the student's name
#             known_face_names.append(os.path.splitext(filename)[0])
#         except IndexError:
#             print(f"Warning: No face found in {filename}. Skipping this file.")
# print("Known faces loaded successfully.")

# # Get a reference to the webcam (use 0 for the default camera)
# video_capture = cv2.VideoCapture(0)

# # Get the current date to create a unique attendance file
# current_date = datetime.now().strftime("%Y-%m-%d")
# attendance_file = f"attendance_{current_date}.csv"

# # List to keep track of students already marked present
# present_students = []

# # Lock for thread-safe operations on shared resources (like the attendance file)
# file_lock = threading.Lock()

# # --- Initialize the CSV file with headers if it's new ---
# def initialize_attendance_file():
#     with file_lock:
#         if not os.path.exists(attendance_file) or os.stat(attendance_file).st_size == 0:
#             with open(attendance_file, 'w', newline='') as f:
#                 writer = csv.writer(f)
#                 writer.writerow(["Name", "Time", "Method"])

# # Call the function to ensure the file is ready
# initialize_attendance_file()


# # --- 2. AI & VIDEO STREAMING FUNCTION ---

# def generate_frames():
#     """Generates frames for the video stream, including face recognition."""
#     process_this_frame = True
#     global present_students

#     while True:
#         success, frame = video_capture.read()
#         if not success:
#             break
#         else:
#             # --- AI Face Recognition Logic (from your code) ---
#             if process_this_frame:
#                 small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
#                 rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

#                 face_locations = face_recognition.face_locations(rgb_small_frame)
#                 face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

#                 face_names = []
#                 for face_encoding in face_encodings:
#                     matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
#                     name = "Unknown"

#                     face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
#                     if len(face_distances) > 0:
#                         best_match_index = np.argmin(face_distances)
#                         if matches[best_match_index]:
#                             name = known_face_names[best_match_index]

#                     face_names.append(name)

#                     # --- Mark Attendance if a known face is detected ---
#                     if name != "Unknown" and name not in present_students:
#                         with file_lock: # Ensure thread-safe writing
#                             with open(attendance_file, 'a', newline='') as f:
#                                 writer = csv.writer(f)
#                                 current_time = datetime.now().strftime("%H:%M:%S")
#                                 writer.writerow([name, current_time, "AI Camera"])
#                         present_students.append(name)
#                         print(f"AI Attendance Marked: {name}")

#             process_this_frame = not process_this_frame

#             # --- Drawing rectangles on the frame ---
#             for (top, right, bottom, left), name in zip(face_locations, face_names):
#                 top *= 4; right *= 4; bottom *= 4; left *= 4
#                 cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
#                 cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
#                 font = cv2.FONT_HERSHEY_DUPLEX
#                 cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

#             # --- Encode and yield the frame ---
#             ret, buffer = cv2.imencode('.jpg', frame)
#             frame = buffer.tobytes()
#             yield (b'--frame\r\n'
#                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# # --- 3. FLASK ROUTES ---

# @app.route('/')
# def index():
#     """Home page with the live video stream."""
#     return render_template('index.html')

# @app.route('/video_feed')
# def video_feed():
#     """Video streaming route."""
#     return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/mark_attendance_rfid', methods=['POST'])
# def mark_attendance_rfid():
#     """Endpoint for RFID reader to send attendance data."""
#     data = request.get_json()
#     student_name = data.get('student_name')

#     if not student_name:
#         return jsonify({"status": "error", "message": "Student name is required"}), 400

#     global present_students
#     if student_name not in present_students:
#         with file_lock: # Ensure thread-safe writing
#             with open(attendance_file, 'a', newline='') as f:
#                 writer = csv.writer(f)
#                 current_time = datetime.now().strftime("%H:%M:%S")
#                 writer.writerow([student_name, current_time, "RFID"])
#         present_students.append(student_name)
#         print(f"RFID Attendance Marked: {student_name}")
#         return jsonify({"status": "success", "message": f"Attendance marked for {student_name}"})
#     else:
#         return jsonify({"status": "info", "message": f"{student_name} is already marked present"})

# @app.route('/attendance')
# def view_attendance():
#     """Page to display the attendance data from the CSV file."""
#     attendance_data = []
#     with open(attendance_file, 'r') as f:
#         reader = csv.reader(f)
#         # Skip header
#         next(reader, None)
#         for row in reader:
#             attendance_data.append(row)
#     return render_template('attendance.html', attendance_data=attendance_data)


# # --- 4. MAIN EXECUTION ---
# if __name__ == '__main__':
#     # Using threaded=True to handle multiple requests (e.g., video stream and RFID)
#     app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)



# # --- Add these imports at the top of your file ---
# from flask import Flask, request, jsonify, render_template, Response
# import requests
# import threading
# import time
# # (your other imports like cv2, mediapipe, etc. remain)
# # (Add any other imports from your original file like speech_recognition)
# import cv2



# # --- Your existing app setup ---
# app = Flask(__name__, template_folder="templates", static_folder="static")

# # ---------------- CORRECTED ESP32 CONFIG ----------------

# # --- IP for the ESP32 that you send commands TO (for gestures, voice, etc.) ---
# # This is the variable your original code uses.
# ESP32_IP = "http://192.168.1.80" # Use the correct IP for your command ESP32

# # --- IP for the ESP32 that you fetch "hi" FROM ---
# # This is the new variable for the polling function.
# ESP32_HI_SERVER_IP = "http://192.168.1.80" # REPLACE WITH YOUR "hi" server ESP32's IP

# # Now, this line will work correctly because ESP32_IP is defined above
# ESP32_COMMAND_ENDPOINT = f"{ESP32_IP}/command"

# # ---------------- DATA STORAGE ----------------
# latest_sensor_data = {}
# latest_hi_message = {"message": "Polling not started yet.", "timestamp": "N/A"}
# message_lock = threading.Lock() # For thread-safe updates

# # ---------------- POLLING FUNCTION (Unchanged) ----------------
# def poll_esp32_for_hi():
#     global latest_hi_message
#     while True:
#         try:
#             response = requests.get(ESP32_HI_SERVER_IP, timeout=3)
#             response.raise_for_status()
#             with message_lock:
#                 latest_hi_message["message"] = response.text.strip()
#                 latest_hi_message["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
#             print(f"Successfully fetched from ESP32: '{latest_hi_message['message']}'")
#         except requests.exceptions.RequestException as e:
#             error_message = f"Error fetching from ESP32: {e}"
#             print(error_message)
#             with message_lock:
#                 latest_hi_message["message"] = "Error"
#                 latest_hi_message["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
#         time.sleep(5)

# #
# # --- YOUR EXISTING CODE (send_command_async, sensor, mediapipe, etc.) GOES HERE ---
# # Make sure all your original functions from the previous version are present here.
# # For example: send_command_async, sensor, get_sensor_data, capture_and_process_loop, etc.
# # I am including them here for completeness.
# #

# # ---------------- COMMAND SENDER ----------------
# last_command_sent = None
# def send_command_async(command: int):
#     global last_command_sent
#     if command == last_command_sent:
#         # print(f"Skipping duplicate command {command}")
#         return
#     def worker():
#         try:
#             response = requests.post(ESP32_COMMAND_ENDPOINT, data=str(command), timeout=5)
#             print(f"Sent command {command} → ESP32, Response: {response.text}")
#         except Exception as e:
#             print(f"Command send failed: {e}")
#     last_command_sent = command
#     threading.Thread(target=worker, daemon=True).start()

# # ---------------- ROUTES ----------------
# @app.route('/')
# def home(): 
#     return render_template("index.html")

# # --- NEW ROUTES TO DISPLAY THE MESSAGE ---
# @app.route('/hi')
# def show_hi_page():
#     with message_lock:
#         message = latest_hi_message["message"]
#         timestamp = latest_hi_message["timestamp"]
#     return f"<h1>Last message fetched from ESP32:</h1><p><b>{message}</b> at {timestamp}</p>"

# @app.route('/get_hi_message')
# def get_hi_message_json():
#     with message_lock:
#         return jsonify(latest_hi_message)

# #
# # --- YOUR OTHER EXISTING ROUTES (/video_feed, /sensor, etc.) would be here ---
# #

# # ---------------- MAIN ----------------
# if __name__ == '__main__':
#     # --- Start the NEW background polling thread ---
#     polling_thread = threading.Thread(target=poll_esp32_for_hi, daemon=True)
#     polling_thread.start()

#     # ---- NOTE: The camera/gesture threads from your code are not included here ----
#     # ---- to keep the example focused, but you would start them here as well. ----
#     # processing_thread = threading.Thread(target=capture_and_process_loop, daemon=True)
#     # processing_thread.start()
#     # gesture_thread = threading.Thread(target=gesture_detection_logic_loop, daemon=True)
#     # gesture_thread.start()
    
#     app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)



from flask import Flask, jsonify, render_template
import requests
import time

# --- App Setup ---
app = Flask(__name__, template_folder="templates")

# ================== CONFIGURATION ==================
# ** IMPORTANT: Change this to the IP address of your ESP32! **
#    You can find this IP in the ESP32's Serial Monitor output after it connects to WiFi.
ESP32_IP = "192.168.1.33"  # <-- CHANGE THIS
ESP32_URL = f"http://{ESP32_IP}/rfid"
# =================================================

def fetch_data_from_esp():
    """
    Fetches the latest RFID data from the ESP32 server.
    Returns a dictionary with the tag data.
    """
    try:
        # Make a GET request to the ESP32, with a timeout of 5 seconds
        # The timeout should be longer than the ESP32's scanning window (2 seconds)
        response = requests.get(ESP32_URL, timeout=5)
        
        # Check if the request was successful (HTTP 200 OK)
        if response.status_code == 200:
            data = response.json()
            data["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
            print(f"Successfully fetched data from ESP32: {data}")
            return data
        else:
            print(f"Error from ESP32: Received Status Code {response.status_code}")
            return {"rfid_tag": "Error", "timestamp": "N/A"}
            
    except requests.exceptions.RequestException as e:
        # This catches network errors (e.g., timeout, ESP32 is offline)
        print(f"Could not connect to ESP32 at {ESP32_URL}. Is it online and connected to WiFi?")
        return {"rfid_tag": "Offline", "timestamp": "N/A"}

@app.route('/')
def home():
    """Renders the main dashboard page."""
    # The initial data is now fetched by the JavaScript in the browser,
    # so we just need to render the template.
    return render_template("index.html")

@app.route('/get_rfid_data')
def get_rfid_data_api():
    """
    API endpoint for the front-end JavaScript to call.
    This fetches fresh data from the ESP32 and returns it as JSON.
    """
    data = fetch_data_from_esp()
    return jsonify(data)

# ---------------- MAIN EXECUTION ----------------
if __name__ == '__main__':
    print("Flask server starting...")
    # Run on host="0.0.0.0" to make it accessible from other devices on your network
    app.run(host="0.0.0.0", port=5000, debug=True)