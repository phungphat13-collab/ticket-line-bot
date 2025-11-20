from flask import Flask, request, jsonify
import os
import logging
import json
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Lấy thông tin từ Environment Variables
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_ACCESS_TOKEN', '')

@app.route("/")
def home():
    return "🤖 Bot is running! ✅"

@app.route("/callback", methods=['POST'])
def callback():
    body = request.get_data(as_text=True)
    logger.info(f"📨 Webhook received")
    
    try:
        data = json.loads(body)
        
        for event in data.get('events', []):
            if event.get('type') == 'message':
                # Lấy thông tin tin nhắn
                reply_token = event.get('replyToken')
                user_message = event.get('message', {}).get('text', '')
                
                logger.info(f"💬 Message: {user_message}")
                
                # Gửi reply
                if reply_token and CHANNEL_ACCESS_TOKEN:
                    send_reply(reply_token, f"Bot đã nhận: {user_message}")
        
        return 'OK'
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return 'Error', 500

def send_reply(reply_token, text):
    """Gửi tin nhắn reply đến user"""
    try:
        url = 'https://api.line.me/v2/bot/message/reply'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'
        }
        data = {
            'replyToken': reply_token,
            'messages': [{'type': 'text', 'text': text}]
        }
        
        response = requests.post(url, headers=headers, json=data)
        logger.info(f"✅ Reply sent: {response.status_code}")
        
    except Exception as e:
        logger.error(f"❌ Reply error: {e}")

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 Starting on port {port}")
    app.run(host='0.0.0.0', port=port)
