
from flask import Flask, jsonify
from threading import Thread
import time
import logging

app = Flask('')

# Configure logging for alive.py
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('alive')

@app.route('/')
def home():
    return "Bot is running and healthy! ✅"

@app.route('/health')
def health_check():
    """Detailed health check endpoint for monitoring"""
    return jsonify({
        "status": "healthy",
        "timestamp": time.time(),
        "uptime": "running"
    })

@app.route('/ping')
def ping():
    """Simple ping endpoint"""
    return "pong"

def run():
    try:
        app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"Flask server error: {e}")
        # Restart after a brief delay
        time.sleep(5)
        run()

def keep_alive():
    logger.info("Starting keep-alive server on port 8080")
    t = Thread(target=run, daemon=True)
    t.start()
    return t
