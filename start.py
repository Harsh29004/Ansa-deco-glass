"""
Quick Start Script for Approval Workflow System
Run this script to set up and start the application
"""
import os
import sys
import subprocess
from pathlib import Path

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def check_python_version():
    """Check if Python version is 3.8+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required. Current version:", sys.version)
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_mongodb():
    """Check if MongoDB is running"""
    try:
        from pymongo import MongoClient
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
        client.server_info()
        print("✅ MongoDB is running")
        return True
    except Exception as e:
        print(f"❌ MongoDB not accessible: {e}")
        print("   Please start MongoDB service")
        return False

def install_dependencies():
    """Install required Python packages"""
    print_header("Installing Dependencies")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed")
        return True
    except Exception as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_directories():
    """Create required directories"""
    print_header("Creating Directories")
    directories = [
        "uploads",
        "uploads/contractor_signatures",
        "uploads/employee_photos",
        "uploads/employee_signatures",
        "uploads/approval_signatures",
        "uploads/idcards",
        "static/images",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directories created")
    return True

def check_env_file():
    """Check if .env file exists"""
    if not os.path.exists('.env'):
        print("⚠️  .env file not found, creating from .env.example")
        if os.path.exists('.env.example'):
            import shutil
            shutil.copy('.env.example', '.env')
            print("✅ .env file created - Please review and update settings")
        else:
            print("❌ .env.example not found")
            return False
    else:
        print("✅ .env file exists")
    return True

def initialize_database():
    """Initialize MongoDB indexes"""
    print_header("Initializing Database")
    try:
        from models import init_database
        init_database()
        print("✅ Database initialized")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        return False

def check_logo():
    """Check if company logo exists"""
    logo_path = "static/images/ansa-deco-glass-original.webp"
    if not os.path.exists(logo_path):
        print(f"⚠️  Company logo not found at {logo_path}")
        print("   Please add your logo or ID cards won't display logo")
    else:
        print("✅ Company logo found")

def run_application():
    """Start the Flask application"""
    print_header("Starting Application")
    print("🚀 Starting Flask server...")
    print("   Access at: http://localhost:5000")
    print("   Press Ctrl+C to stop\n")
    
    try:
        subprocess.call([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n\n✅ Application stopped")

def main():
    """Main setup and start function"""
    print_header("Approval Workflow System - Quick Start")
    
    # Check prerequisites
    if not check_python_version():
        return
    
    if not check_mongodb():
        print("\n💡 To start MongoDB:")
        print("   Windows: net start MongoDB")
        print("   Linux: sudo systemctl start mongodb")
        return
    
    # Setup
    if not create_directories():
        return
    
    if not check_env_file():
        return
    
    if not install_dependencies():
        return
    
    if not initialize_database():
        return
    
    check_logo()
    
    # Start application
    print("\n" + "="*60)
    print("✅ Setup complete! Starting application...")
    print("="*60)
    
    input("\nPress Enter to start the server...")
    run_application()

if __name__ == "__main__":
    main()
