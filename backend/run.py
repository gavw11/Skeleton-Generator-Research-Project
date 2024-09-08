from waitress import serve
import os
from app import app  # Ensure this imports your WSGI application correctly

if __name__ == "__main__":
    port = int(os.getenv('PORT', 8000))  # Default to 8000 if PORT is not set
    serve(app, host='0.0.0.0', port=port)
