from app import app

# This is the WSGI entry point for Vercel
application = app

if __name__ == "__main__":
    app.run()
