from flask import Flask, request, jsonify
import os
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route("/")
def home():
    return "🤖 Bot is running! ✅"

@app.route("/callback", methods=['POST', 'GET'])
def callback():
    if request.method == 'GET':
        return "Callback endpoint - use POST"
    
    # POST request từ LINE
    body = request.get_data(as_text=True)
    logger.info(f"📨 Webhook received")
    
    try:
        data = json.loads(body)
        events = data.get('events', [])
        logger.info(f"✅ Processed {len(events)} events")
        
        for event in events:
            if event.get('type') == 'message':
                message = event.get('message', {})
                text = message.get('text', '')
                logger.info(f"💬 Message: {text}")
        
        return 'OK'
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return 'Error', 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
