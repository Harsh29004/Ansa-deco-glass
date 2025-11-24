"""
WSGI Entry Point for Vercel Deployment
"""
from app import app as application

# Vercel expects 'app' or 'application' variable
app = application

if __name__ == "__main__":
    application.run()
