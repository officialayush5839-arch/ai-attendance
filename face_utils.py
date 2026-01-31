import face_recognition
import cv2
import numpy as np

class FaceRecognitionSystem:
    def __init__(self, tolerance=0.6):
        self.known_face_encodings = []
        self.known_face_details = []
        self.tolerance = tolerance

    def load_students(self, students_list):
        self.known_face_encodings = []
        self.known_face_details = []

        for student in students_list:
            try:
                self.known_face_encodings.append(student['encoding'])
                self.known_face_details.append({
                    'roll_number': student['roll_number'],
                    'name': student['name'],
                    'email': student['email']
                })
            except:
                continue

    def process_frame(self, frame):
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        return face_locations, face_encodings

    def recognize_faces(self, frame):
        face_locations, face_encodings = self.process_frame(frame)
        recognized_students = []

        for face_encoding, face_location in zip(face_encodings, face_locations):
            if len(self.known_face_encodings) == 0:
                continue

            matches = face_recognition.compare_faces(
                self.known_face_encodings, 
                face_encoding, 
                tolerance=self.tolerance
            )
            face_distances = face_recognition.face_distance(
                self.known_face_encodings, 
                face_encoding
            )

            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    student = self.known_face_details[best_match_index]
                    recognized_students.append({
                        'student': student,
                        'location': face_location,
                        'confidence': 1 - face_distances[best_match_index]
                    })

        return recognized_students

    def get_face_encoding(self, image_path):
        try:
            image = face_recognition.load_image_file(image_path)
            face_encodings = face_recognition.face_encodings(image)

            if len(face_encodings) == 0:
                return None, "No face detected! Please ensure your face is clearly visible."
            elif len(face_encodings) > 1:
                return None, "Multiple faces detected! Please ensure only one person is in frame."
            else:
                return face_encodings[0], None

        except Exception as e:
            return None, f"Error processing image: {str(e)}"
