# SRM Smart Attendance System 🤖

AI-powered facial recognition attendance system for SRM University.

## Features
- ✨ Automatic face recognition
- 📧 Email notifications
- 📊 Google Sheets integration
- 🎓 Student registration portal
- 🔒 Secure data storage

## Quick Deploy

### Render.com (Recommended)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

### Environment Variables
| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL/SQLite connection string | Yes |
| `EMAIL_USER` | Gmail address for notifications | Optional |
| `EMAIL_PASS` | Gmail App Password | Optional |
| `SECRET_KEY` | Flask secret key | Yes |

## Google Sheets Setup
1. Create service account in Google Cloud Console
2. Download `credentials.json`
3. Place in root directory
4. Share spreadsheet with service account email

## License
MIT License - SRM University Project
