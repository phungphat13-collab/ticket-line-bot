from flask import Flask, request, jsonify
import os
import logging
import hmac
import hashlib
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Lấy Channel Secret từ environment
CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET', '')

@app.route("/")
def home():
    return "🤖 Bot is running! ✅"

@app.route("/callback", methods=['POST'])
def callback():
    try:
        # Get signature từ header
        signature = request.headers.get('X-Line-Signature', '')
        
        # Get request body
        body = request.get_data(as_text=True)
        logger.info(f"📨 Webhook received: {body}")
        
        # Verify signature (bảo mật)
        hash = hmac.new(
            CHANNEL_SECRET.encode('utf-8'),
            body.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        if signature != hash:
            logger.error("❌ Invalid signature")
            return 'Signature verification failed', 400
        
        # Parse JSON data
        data = json.loads(body)
        
        # Xử lý events
        for event in data.get('events', []):
            if event.get('type') == 'message':
                handle_message(event)
        
        logger.info("✅ Webhook processed successfully")
        return 'OK'
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return 'Error', 500

def handle_message(event):
    """Xử lý tin nhắn từ user"""
    try:
        user_message = event.get('message', {}).get('text', '')
        reply_token = event.get('replyToken', '')
        
        logger.info(f"💬 Message from user: {user_message}")
        
        # Gửi reply (cần implement thêm)
        # Ở bước này, ít nhất chúng ta biết webhook đang hoạt động
        
    except Exception as e:
        logger.error(f"❌ Error handling message: {e}")

@app.route("/test", methods=['GET'])
def test():
    return jsonify({"status": "active", "message": "Bot is working!"})

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 Starting on port {port}")
    app.run(host='0.0.0.0', port=port)
