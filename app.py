from flask import Flask, request, jsonify
import os
import logging
import json
import requests
import threading
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = os.getenv('LINE_ACCESS_TOKEN', '')
YOUR_COMPUTER_URL = "https://condonable-insuperable-cathie.ngrok-free.dev"
RENDER = os.getenv('RENDER', False)  # Render tự set biến này

def keep_alive():
    """Tự ping server để ngăn sleep"""
    time.sleep(10)  # Đợi server khởi động
    
    while True:
        try:
            # Ping chính server
            requests.get(f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME', '')}/", timeout=10)
            logger.info("🔄 Keep-alive ping sent")
        except Exception as e:
            logger.error(f"Keep-alive error: {e}")
        
        # Ping mỗi 5 phút (Render sleep sau 15 phút không hoạt động)
        time.sleep(300)

@app.route("/")
def home():
    return "🤖 Ticket Bot Gateway is running! ✅"

@app.route("/health")
def health_check():
    return jsonify({"status": "healthy", "timestamp": time.time()})

@app.route("/callback", methods=['POST'])
def callback():
    # ... giữ nguyên code callback của bạn ...

# Khởi động keep-alive khi start
if RENDER:
    @app.before_first_request
    def start_keep_alive():
        thread = threading.Thread(target=keep_alive, daemon=True)
        thread.start()
        logger.info("🚀 Keep-alive thread started")

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 Starting on port {port}")
    
    # Start keep-alive ngay lập tức nếu trên Render
    if RENDER:
        thread = threading.Thread(target=keep_alive, daemon=True)
        thread.start()
    
    app.run(host='0.0.0.0', port=port)
