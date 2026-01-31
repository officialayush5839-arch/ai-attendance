import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class EmailService:
    def __init__(self, sender_email, sender_password, smtp_server='smtp.gmail.com', smtp_port=587):
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

    def send_mail(self, recipient, subject, body, html=None):
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = recipient

            msg.attach(MIMEText(body, 'plain'))

            if html:
                msg.attach(MIMEText(html, 'html'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.sendmail(self.sender_email, recipient, msg.as_string())
            server.quit()
            return True
        except Exception as e:
            print(f"Email Error: {e}")
            return False

    def send_attendance_confirmation(self, student_email, student_name, roll_number, subject):
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; padding: 30px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
                <div style="text-align: center; border-bottom: 3px solid #4CAF50; padding-bottom: 20px; margin-bottom: 20px;">
                    <h1 style="color: #4CAF50; margin: 0;">SRM Attendance System</h1>
                    <p style="color: #666; margin: 10px 0 0 0;">Automated Attendance Confirmation</p>
                </div>

                <div style="background: #f9f9f9; padding: 20px; border-radius: 5px; margin-bottom: 20px;">
                    <h2 style="color: #333; margin-top: 0;">Hello {student_name},</h2>
                    <p style="font-size: 16px; line-height: 1.6; color: #555;">
                        Your attendance has been successfully recorded for today's lecture.
                    </p>
                </div>

                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <tr style="background: #4CAF50; color: white;">
                        <td style="padding: 12px; border: 1px solid #ddd; font-weight: bold;">Detail</td>
                        <td style="padding: 12px; border: 1px solid #ddd; font-weight: bold;">Information</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd;">Roll Number</td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{roll_number}</td>
                    </tr>
                    <tr style="background: #f9f9f9;">
                        <td style="padding: 10px; border: 1px solid #ddd;">Subject</td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{subject}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd;">Date</td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{datetime.now().strftime('%Y-%m-%d')}</td>
                    </tr>
                    <tr style="background: #f9f9f9;">
                        <td style="padding: 10px; border: 1px solid #ddd;">Time</td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{datetime.now().strftime('%H:%M:%S')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd;">Status</td>
                        <td style="padding: 10px; border: 1px solid #ddd; color: #4CAF50; font-weight: bold;">✓ PRESENT</td>
                    </tr>
                </table>

                <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #999; font-size: 12px;">
                    <p>This is an automated message from SRM Attendance System.<br>Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """

        body = f"""
        Hello {student_name},

        Your attendance has been marked for {subject} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.
        Roll Number: {roll_number}
        Status: PRESENT

        - SRM Attendance System
        """

        return self.send_mail(student_email, f"Attendance Marked - {subject}", body, html)
