from flask import Flask, request, jsonify
import os
import logging
import json
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = os.getenv('LINE_ACCESS_TOKEN', '')
# URL của server automation thật
AUTOMATION_SERVER_URL = "http://your-automation-server.com"  # Thay bằng URL thật

@app.route("/")
def home():
    return "🤖 Ticket Bot Gateway is running! ✅"

@app.route("/callback", methods=['POST'])
def callback():
    body = request.get_data(as_text=True)
    
    try:
        data = json.loads(body)
        
        for event in data.get('events', []):
            if event.get('type') == 'message':
                user_id = event.get('source', {}).get('userId')
                reply_token = event.get('replyToken')
                user_message = event.get('message', {}).get('text', '').strip()
                
                logger.info(f"💬 From {user_id}: {user_message}")
                handle_user_command(user_id, reply_token, user_message)
        
        return 'OK'
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return 'Error', 500

def handle_user_command(user_id, reply_token, message):
    """Xử lý lệnh và gửi đến server automation thật"""
    try:
        if message.lower() == "help":
            reply_text = """🤖 TICKET AUTOMATION BOT - REAL MODE

📝 LỆNH THẬT:
• help - Hướng dẫn
• login username:password - Chạy automation THẬT trên website
• stop - Dừng automation
• status - Trạng thái

⚠️ LƯU Ý: Automation THẬT sẽ:
- Truy cập newticket.tgdd.vn
- Đăng nhập THẬT
- Xử lý ticket THẬT
- Gửi kết quả THẬT qua LINE"""
            
        elif message.lower().startswith("login "):
            credentials = message[6:]
            if ":" in credentials:
                username, password = credentials.split(":", 1)
                
                # Gửi lệnh đến server automation thật
                send_to_automation_server(user_id, username, password)
                reply_text = "🚀 ĐÃ GỬI LỆNH ĐẾN SERVER AUTOMATION THẬT! Bot sẽ báo cáo kết quả thực tế..."
            else:
                reply_text = "❌ Sai định dạng! Ví dụ: login username:password"
                
        elif message.lower() == "status":
            reply_text = "🟢 Hệ thống sẵn sàng - Kết nối automation server"
                
        else:
            reply_text = f"Bot nhận được: {message}\nGửi 'help' để chạy automation THẬT"
        
        send_reply(reply_token, reply_text)
        
    except Exception as e:
        logger.error(f"Command error: {e}")
        send_reply(reply_token, "❌ Có lỗi xảy ra!")

def send_to_automation_server(user_id, username, password):
    """Gửi lệnh đến server automation thật"""
    try:
        data = {
            'user_id': user_id,
            'username': username,
            'password': password,
            'line_token': CHANNEL_ACCESS_TOKEN
        }
        response = requests.post(f"{AUTOMATION_SERVER_URL}/start", json=data, timeout=5)
        logger.info(f"📤 Sent to automation server: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Cannot connect to automation server: {e}")
        send_message(user_id, "❌ Không thể kết nối đến server automation!")

def send_message(user_id, text):
    """Gửi tin nhắn đến user"""
    try:
        url = 'https://api.line.me/v2/bot/message/push'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'
        }
        data = {
            'to': user_id,
            'messages': [{'type': 'text', 'text': text}]
        }
        requests.post(url, headers=headers, json=data)
        logger.info(f"📤 Sent to {user_id}: {text}")
    except Exception as e:
        logger.error(f"Send message error: {e}")

def send_reply(reply_token, text):
    """Gửi tin nhắn reply"""
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
        requests.post(url, headers=headers, json=data)
    except Exception as e:
        logger.error(f"Reply error: {e}")

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 Starting on port {port}")
    app.run(host='0.0.0.0', port=port)
