"""
Simple launcher for the ANSA Deco Glass Approval Workflow System
This launcher handles the import gracefully
"""
import os
import sys

# Suppress WeasyPrint warnings
import warnings
warnings.filterwarnings('ignore')

if __name__ == '__main__':
    from app import app
    
    print("=" * 60)
    print("ANSA Deco Glass - Approval Workflow System")
    print("=" * 60)
    print(f"Server starting...")
    print(f"Access the application at: http://localhost:5000")
    print(f"Press CTRL+C to stop the server")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
