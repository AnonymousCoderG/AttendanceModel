# import cv2
# import face_recognition
# import os
# import csv
# from datetime import datetime

# # Path to the directory containing student images
# images_path = "images"

# # Lists to store known face encodings and names
# known_face_encodings = []
# known_face_names = []

# # Load student images and learn how to recognize them
# print("Loading known faces...")
# for filename in os.listdir(images_path):
#     if filename.endswith((".jpg", ".png", ".jpeg")):
#         # Load the image
#         image_path = os.path.join(images_path, filename)
#         student_image = face_recognition.load_image_file(image_path)

#         # Get the face encoding for the first face found in the image
#         try:
#             student_face_encoding = face_recognition.face_encodings(student_image)[0]
#             known_face_encodings.append(student_face_encoding)
#             # Get the student's name from the filename (without extension)
#             known_face_names.append(os.path.splitext(filename)[0])
#         except IndexError:
#             print(f"Warning: No face found in {filename}. Skipping this file.")

# print("Known faces loaded successfully.")

# # Get a reference to the webcam
# video_capture = cv2.VideoCapture(0)

# # List to keep track of students already marked present in the current session
# present_students = []

# # Get the current date to create a unique attendance file for the day
# current_date = datetime.now().strftime("%Y-%m-%d")
# attendance_file = f"attendance_{current_date}.csv"

# # Open the attendance file in append mode
# with open(attendance_file, 'a', newline='') as f:
#     writer = csv.writer(f)
#     # Write the header if the file is new
#     if os.stat(attendance_file).st_size == 0:
#         writer.writerow(["Name", "Time"])

#     while True:
#         # Grab a single frame of video
#         ret, frame = video_capture.read()

#         # Resize frame for faster processing
#         small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

#         # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
#         rgb_small_frame = small_frame[:, :, ::-1]

#         # Find all the faces and face encodings in the current frame of video
#         face_locations = face_recognition.face_locations(rgb_small_frame)
#         face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

#         for face_encoding in face_encodings:
#             # See if the face is a match for the known faces
#             matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
#             name = "Unknown"

#             # Use the known face with the smallest distance to the new face
#             face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
#             best_match_index = -1
#             if True in matches:
#               best_match_index = min([i for i, match in enumerate(matches) if match])
#               name = known_face_names[best_match_index]

#             # If a match is found and the student is not already marked present
#             if name != "Unknown" and name not in present_students:
#                 current_time = datetime.now().strftime("%H:%M:%S")
#                 writer.writerow([name, current_time])
#                 f.flush()  # Ensure the data is written to the file immediately
#                 present_students.append(name)
#                 print(f"Attendance marked for {name} at {current_time}")

#         # Display the results
#         for (top, right, bottom, left), name in zip([(t*4, r*4, b*4, l*4) for t, r, b, l in face_locations], [known_face_names[min([i for i, match in enumerate(face_recognition.compare_faces(known_face_encodings, enc)) if match])] if True in face_recognition.compare_faces(known_face_encodings, enc) else "Unknown" for enc in face_encodings]):
#             # Draw a box around the face
#             cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

#             # Draw a label with a name below the face
#             cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
#             font = cv2.FONT_HERSHEY_DUPLEX
#             cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

#         # Display the resulting image
#         cv2.imshow('Video', frame)

#         # Hit 'q' on the keyboard to quit!
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

# # Release handle to the webcam
# video_capture.release()
# cv2.destroyAllWindows()


#above model is basic working model works best for gouri but for gouri and yash both gives flashing

# import cv2
# import face_recognition
# import os
# import csv
# from datetime import datetime

# # Path to the directory containing student images
# images_path = "images"

# # Lists to store known face encodings and names
# known_face_encodings = []
# known_face_names = []

# # Load student images and learn how to recognize them
# print("Loading known faces...")
# for filename in os.listdir(images_path):
#     if filename.endswith((".jpg", ".png", ".jpeg")):
#         # Load the image
#         image_path = os.path.join(images_path, filename)
#         student_image = face_recognition.load_image_file(image_path)

#         # Get the face encoding for the first face found in the image
#         try:
#             student_face_encoding = face_recognition.face_encodings(student_image)[0]
#             known_face_encodings.append(student_face_encoding)
#             # Get the student's name from the filename (without extension)
#             known_face_names.append(os.path.splitext(filename)[0])
#         except IndexError:
#             print(f"Warning: No face found in {filename}. Skipping this file.")

# print("Known faces loaded successfully.")

# # Get a reference to the webcam
# video_capture = cv2.VideoCapture(0)

# # List to keep track of students already marked present in the current session
# present_students = []

# # Get the current date to create a unique attendance file for the day
# current_date = datetime.now().strftime("%Y-%m-%d")
# attendance_file = f"attendance_{current_date}.csv"

# # NEW: Variables to store the last known locations and names for smoother display
# last_known_locations = []
# last_known_names = []

# # Open the attendance file in append mode
# with open(attendance_file, 'a', newline='') as f:
#     writer = csv.writer(f)
#     # Write the header if the file is new
#     if os.stat(attendance_file).st_size == 0:
#         writer.writerow(["Name", "Time"])

#     while True:
#         # Grab a single frame of video
#         ret, frame = video_capture.read()

#         # Resize frame for faster processing
#         small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

#         # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
#         rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

#         # Find all the faces and face encodings in the current frame of video
#         face_locations = face_recognition.face_locations(rgb_small_frame)
#         face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

#         current_frame_names = []
#         for face_encoding in face_encodings:
#             # See if the face is a match for the known faces
#             matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
#             name = "Unknown"

#             # Use the known face with the smallest distance to the new face
#             face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
#             if len(face_distances) > 0:
#                 best_match_index = face_distances.argmin()
#                 if matches[best_match_index]:
#                     name = known_face_names[best_match_index]

#             current_frame_names.append(name)

#             # If a match is found and the student is not already marked present
#             if name != "Unknown" and name not in present_students:
#                 current_time = datetime.now().strftime("%H:%M:%S")
#                 writer.writerow([name, current_time])
#                 f.flush()  # Ensure the data is written to the file immediately
#                 present_students.append(name)
#                 print(f"Attendance marked for {name} at {current_time}")

#         # NEW: If faces were detected in this frame, update our "memory"
#         if len(face_locations) > 0:
#             last_known_locations = face_locations
#             last_known_names = current_frame_names
        
#         # Display the results using the last known good data to prevent flashing
#         for (top, right, bottom, left), name in zip(last_known_locations, last_known_names):
#             # Scale back up face locations since the frame we detected in was scaled to 1/4 size
#             top *= 4
#             right *= 4
#             bottom *= 4
#             left *= 4

#             # Draw a box around the face
#             cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

#             # Draw a label with a name below the face
#             cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
#             font = cv2.FONT_HERSHEY_DUPLEX
#             cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

#         # Display the resulting image
#         cv2.imshow('Video', frame)

#         # Hit 'q' on the keyboard to quit!
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

# # Release handle to the webcam
# video_capture.release()
# cv2.destroyAllWindows()


#above code works perfect for both yash and gouri but the frame is stuck until new person is not in the frame




import cv2
import face_recognition
import os
import csv
from datetime import datetime
import numpy as np

# --- 1. SETUP ---

# Path to the directory containing student images
images_path = "images"

# Lists to store known face encodings and names
known_face_encodings = []
known_face_names = []

# Load student images and learn how to recognize them
print("Loading known faces...")
for filename in os.listdir(images_path):
    if filename.endswith((".jpg", ".png", ".jpeg")):
        image_path = os.path.join(images_path, filename)
        student_image = face_recognition.load_image_file(image_path)
        try:
            student_face_encoding = face_recognition.face_encodings(student_image)[0]
            known_face_encodings.append(student_face_encoding)
            known_face_names.append(os.path.splitext(filename)[0])
        except IndexError:
            print(f"Warning: No face found in {filename}. Skipping this file.")
print("Known faces loaded successfully.")

# Get a reference to the webcam
video_capture = cv2.VideoCapture(0)

# Get the current date to create a unique attendance file for the day
current_date = datetime.now().strftime("%Y-%m-%d")
attendance_file = f"attendance_{current_date}.csv"

# --- 2. INITIALIZE VARIABLES FOR THE LOOP ---

# List to keep track of students already marked present in the current session
present_students = []

# Variables to hold the state between frames
face_locations = []
face_names = []

# This is a toggle to only process every other frame
process_this_frame = True

# Open the attendance file in append mode
with open(attendance_file, 'a', newline='') as f:
    writer = csv.writer(f)
    if os.stat(attendance_file).st_size == 0:
        writer.writerow(["Name", "Time"])

    # --- 3. MAIN LOOP ---
    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        # --- 4. ALTERNATE FRAME PROCESSING ---
        # Only process every other frame of video to save time
        if process_this_frame:
            # Resize frame for faster processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            # Convert the image from BGR color (OpenCV) to RGB color (face_recognition)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            # Find all the faces and face encodings in the current frame
            current_face_locations = face_recognition.face_locations(rgb_small_frame)
            current_face_encodings = face_recognition.face_encodings(rgb_small_frame, current_face_locations)

            # Reset the list of names for this new processing cycle
            face_names = []
            for face_encoding in current_face_encodings:
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                if len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = known_face_names[best_match_index]

                face_names.append(name)

                # If a match is found and the student is not already marked present
                if name != "Unknown" and name not in present_students:
                    current_time = datetime.now().strftime("%H:%M:%S")
                    writer.writerow([name, current_time])
                    f.flush()
                    present_students.append(name)
                    print(f"Attendance marked for {name} at {current_time}")
            
            # Update the main face_locations variable
            face_locations = current_face_locations

        # Toggle for the next frame
        process_this_frame = not process_this_frame

        # --- 5. DISPLAY RESULTS (EVERY FRAME) ---
        # This part runs every frame, using the results from the last processed frame.
        # This creates a smooth, non-flashing output.
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# --- 6. CLEANUP ---
video_capture.release()
cv2.destroyAllWindows()