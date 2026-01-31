import os
import base64
import io
import numpy as np
import cv2
from PIL import Image
from flask import Flask, render_template, request, jsonify
from datetime import datetime

from config import Config
from database import Database
from face_utils import FaceRecognitionSystem
from email_service import EmailService
from sheets_service import SheetsService

app = Flask(__name__)
app.config.from_object(Config)

# Initialize services
db = Database(app.config['DATABASE_URL'])
face_system = FaceRecognitionSystem()

email_service = None
if app.config.get('EMAIL_USER') and app.config.get('EMAIL_PASS'):
    email_service = EmailService(
        app.config['EMAIL_USER'], 
        app.config['EMAIL_PASS']
    )

sheets_service = None
if os.path.exists('credentials.json'):
    sheets_service = SheetsService()

def reload_students():
    students = db.get_all_students()
    face_system.load_students(students)
    return students

students = reload_students()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/attendance')
def attendance_page():
    return render_template('attendance.html')

@app.route('/api/register', methods=['POST'])
def register_student():
    try:
        data = request.form
        roll_number = data.get('roll_number', '').strip().upper()
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        branch = data.get('branch', '').strip().upper()
        section = data.get('section', '').strip().upper()

        if not all([roll_number, name, email, branch, section]):
            return jsonify({'success': False, 'message': 'All fields are required!'})

        image_path = None
        if 'image_data' in data and data['image_data']:
            image_data = data['image_data'].split(',')[1]
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))

            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{roll_number}.jpg")
            image.save(image_path)

        if not image_path or not os.path.exists(image_path):
            return jsonify({'success': False, 'message': 'No image captured!'})

        encoding, error = face_system.get_face_encoding(image_path)
        if error:
            if os.path.exists(image_path):
                os.remove(image_path)
            return jsonify({'success': False, 'message': error})

        success, message = db.register_student(
            roll_number, name, email, branch, section, encoding
        )

        if success:
            global students
            students = reload_students()

            if email_service:
                try:
                    email_service.send_mail(
                        email,
                        "Welcome to SRM Smart Attendance",
                        f"Hello {name},\n\nYou have been successfully registered.\nRoll Number: {roll_number}"
                    )
                except:
                    pass

            return jsonify({
                'success': True, 
                'message': 'Registration successful!',
                'student': {'roll_number': roll_number, 'name': name}
            })
        else:
            if os.path.exists(image_path):
                os.remove(image_path)
            return jsonify({'success': False, 'message': message})

    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'})

@app.route('/api/recognize', methods=['POST'])
def recognize_face():
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'success': False, 'message': 'No image data received'})

        image_data = data['image'].split(',')[1]
        subject = data.get('subject', 'General')

        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        recognized = face_system.recognize_faces(frame)

        if not recognized:
            return jsonify({'success': True, 'results': [], 'message': 'No faces recognized'})

        results = []
        for person in recognized:
            student = person['student']
            success, message = db.mark_attendance(
                student['roll_number'],
                student['name'],
                subject
            )

            result_data = {
                'name': student['name'],
                'roll_number': student['roll_number'],
                'confidence': round(float(person['confidence']), 2),
                'attendance_marked': success,
                'message': message
            }

            if success:
                full_student = next(
                    (s for s in students if s['roll_number'] == student['roll_number']),
                    None
                )

                if full_student:
                    if sheets_service:
                        try:
                            sheets_service.record_attendance(
                                student['roll_number'],
                                student['name'],
                                subject,
                                full_student['branch'],
                                full_student['section'],
                                student['email']
                            )
                        except:
                            pass

                    if email_service:
                        try:
                            email_service.send_attendance_confirmation(
                                student['email'],
                                student['name'],
                                student['roll_number'],
                                subject
                            )
                        except:
                            pass

            results.append(result_data)

        return jsonify({'success': True, 'results': results})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/attendance/today')
def today_attendance():
    try:
        date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        records = db.get_attendance_report(date)

        formatted = []
        for record in records:
            formatted.append({
                'id': record[0],
                'roll_number': record[1],
                'name': record[2],
                'subject': record[3],
                'timestamp': record[4],
                'status': record[5]
            })

        return jsonify({'success': True, 'records': formatted})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/students')
def get_students():
    return jsonify({
        'success': True,
        'count': len(students),
        'students': [{'roll_number': s['roll_number'], 'name': s['name'], 'branch': s['branch']} for s in students]
    })

@app.route('/api/stats')
def get_stats():
    try:
        total_students = len(students)
        today_count = len(db.get_attendance_report(datetime.now().strftime('%Y-%m-%d')))

        return jsonify({
            'success': True,
            'total_students': total_students,
            'today_attendance': today_count
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('DEBUG', 'False').lower() == 'true')
