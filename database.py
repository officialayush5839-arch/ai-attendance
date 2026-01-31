import sqlite3
import pickle
import psycopg2
import os
from datetime import datetime

class Database:
    def __init__(self, database_url):
        self.database_url = database_url
        self.is_postgres = database_url.startswith('postgresql://')
        self.init_db()

    def get_connection(self):
        if self.is_postgres:
            return psycopg2.connect(self.database_url, sslmode='require')
        else:
            return sqlite3.connect('attendance.db', check_same_thread=False)

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        if self.is_postgres:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    id SERIAL PRIMARY KEY,
                    roll_number VARCHAR(50) UNIQUE NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) NOT NULL,
                    branch VARCHAR(50) NOT NULL,
                    section VARCHAR(10) NOT NULL,
                    face_encoding BYTEA NOT NULL,
                    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS attendance (
                    id SERIAL PRIMARY KEY,
                    roll_number VARCHAR(50) NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    subject VARCHAR(100) NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(20) DEFAULT 'Present'
                )
            ''')
        else:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    roll_number TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    branch TEXT NOT NULL,
                    section TEXT NOT NULL,
                    face_encoding BLOB NOT NULL,
                    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    roll_number TEXT NOT NULL,
                    name TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'Present'
                )
            ''')

        conn.commit()
        conn.close()

    def register_student(self, roll_number, name, email, branch, section, face_encoding):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            encoding_bytes = pickle.dumps(face_encoding)

            if self.is_postgres:
                cursor.execute('''
                    INSERT INTO students (roll_number, name, email, branch, section, face_encoding)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (roll_number, name, email, branch, section, psycopg2.Binary(encoding_bytes)))
            else:
                cursor.execute('''
                    INSERT INTO students (roll_number, name, email, branch, section, face_encoding)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (roll_number, name, email, branch, section, encoding_bytes))

            conn.commit()
            conn.close()
            return True, "Student registered successfully!"

        except (sqlite3.IntegrityError, psycopg2.IntegrityError):
            return False, "Roll number already exists!"
        except Exception as e:
            return False, str(e)

    def get_all_students(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT roll_number, name, email, branch, section, face_encoding FROM students')
        rows = cursor.fetchall()

        students = []
        for row in rows:
            try:
                encoding = pickle.loads(row[5])
                students.append({
                    'roll_number': row[0],
                    'name': row[1],
                    'email': row[2],
                    'branch': row[3],
                    'section': row[4],
                    'encoding': encoding
                })
            except:
                continue

        conn.close()
        return students

    def mark_attendance(self, roll_number, name, subject):
        conn = self.get_connection()
        cursor = conn.cursor()

        today = datetime.now().strftime('%Y-%m-%d')

        if self.is_postgres:
            cursor.execute('''
                SELECT id FROM attendance 
                WHERE roll_number = %s AND DATE(timestamp) = %s AND subject = %s
            ''', (roll_number, today, subject))
        else:
            cursor.execute('''
                SELECT id FROM attendance 
                WHERE roll_number = ? AND date(timestamp) = ? AND subject = ?
            ''', (roll_number, today, subject))

        if cursor.fetchone():
            conn.close()
            return False, "Already marked present today!"

        if self.is_postgres:
            cursor.execute('''
                INSERT INTO attendance (roll_number, name, subject)
                VALUES (%s, %s, %s)
            ''', (roll_number, name, subject))
        else:
            cursor.execute('''
                INSERT INTO attendance (roll_number, name, subject)
                VALUES (?, ?, ?)
            ''', (roll_number, name, subject))

        conn.commit()
        conn.close()
        return True, "Attendance marked successfully!"

    def get_attendance_report(self, date=None):
        conn = self.get_connection()
        cursor = conn.cursor()

        if date:
            if self.is_postgres:
                cursor.execute('''
                    SELECT * FROM attendance WHERE DATE(timestamp) = %s
                    ORDER BY timestamp DESC
                ''', (date,))
            else:
                cursor.execute('''
                    SELECT * FROM attendance WHERE date(timestamp) = ?
                    ORDER BY timestamp DESC
                ''', (date,))
        else:
            cursor.execute('SELECT * FROM attendance ORDER BY timestamp DESC LIMIT 100')

        results = cursor.fetchall()
        conn.close()
        return results
