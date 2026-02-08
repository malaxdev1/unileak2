"""
WSGI entry point para Vercel
"""
from app import app

# Para Vercel
app = app

if __name__ == "__main__":
    app.run()
