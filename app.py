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

@app.route("/callback", methods=['POST', 'GET'])
def callback():
    if request.method == 'GET':
        return jsonify({
            "status": "callback endpoint", 
            "message": "Use POST for LINE webhook",
            "channel_secret_set": bool(CHANNEL_SECRET)
        })
    
    # POST request từ LINE
    try:
        signature = request.headers.get('X-Line-Signature', '')
        body = request.get_data(as_text=True)
        logger.info(f"📨 Webhook received")
        
        # Verify signature
        if CHANNEL_SECRET:
            hash = hmac.new(
                CHANNEL_SECRET.encode('utf-8'),
                body.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            if signature != hash:
                logger.error("❌ Invalid signature")
                return 'Signature verification failed', 400
        
        # Parse và xử lý events
        data = json.loads(body)
        logger.info(f"✅ Processed {len(data.get('events', []))} events")
        
        return 'OK'
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return 'Error', 500

@app.route("/test", methods=['GET'])
def test():
    return jsonify({"status": "active", "message": "Bot is working!"})

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 Starting on port {port}")
    app.run(host='0.0.0.0', port=port)
