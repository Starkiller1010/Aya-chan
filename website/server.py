from flask import Flask, render_template
from threading import Thread

app = Flask('')

@app.route('/')
def home():
  return render_template('index.html')

@app.route('/health')
def service_status():
  return "Service is up"

@app.route('/admin')
def admin_home():
  return render_template('admin.html')

def run():
  app.run(host='0.0.0.0', port=8080)

def init_website():
  t = Thread(target=run)
  t.start()