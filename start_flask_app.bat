@echo off
set FLASK_APP=app.py
set FLASK_ENV=production
flask run --host=http:192.168.0.12 --port=5000
