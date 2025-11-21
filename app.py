from flask import Flask, request, jsonify
import os
import logging
import json
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = os.getenv('LINE_ACCESS_TOKEN', '')
# URL của máy tính bạn (cần public IP hoặc dùng ngrok)
YOUR_COMPUTER_URL = "https://condonable-insuperable-cathie.ngrok-free.dev"  # Thay bằng IP thật

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
    """Xử lý lệnh và gửi đến máy tính của bạn"""
    try:
        if message.lower() == "help":
            reply_text = """🤖 TICKET AUTOMATION - LOCAL MODE

📝 LỆNH:
• help - Hướng dẫn
• login username:password - Đăng nhập & chạy auto ticket trên máy bạn
• status - Trạng thái

🔐 CÁCH HOẠT ĐỘNG:
1. Bot nhận lệnh từ LINE
2. Mở Chrome trên máy bạn
3. Chạy automation ticket THẬT
4. Gửi kết quả về LINE"""
            
        elif message.lower().startswith("login "):
            credentials = message[6:]
            if ":" in credentials:
                username, password = credentials.split(":", 1)
                
                # Gửi lệnh đến máy tính của bạn
                success = send_to_local_computer(user_id, username, password)
                if success:
                    reply_text = "🚀 ĐÃ GỬI LỆNH ĐẾN MÁY TÍNH CỦA BẠN! Đang mở Chrome và chạy automation..."
                else:
                    reply_text = "❌ Không thể kết nối đến máy tính của bạn. Kiểm tra kết nối."
            else:
                reply_text = "❌ Sai định dạng! Ví dụ: login username:password"
                
        elif message.lower() == "status":
            reply_text = "🟢 Bot sẵn sàng - Chờ lệnh từ LINE"
                
        else:
            reply_text = f"Bot nhận được: {message}\nGửi 'help' để chạy automation"
        
        send_reply(reply_token, reply_text)
        
    except Exception as e:
        logger.error(f"Command error: {e}")
        send_reply(reply_token, "❌ Có lỗi xảy ra!")

def send_to_local_computer(user_id, username, password):
    """Gửi lệnh đến máy tính của bạn"""
    try:
        data = {
            'user_id': user_id,
            'username': username,
            'password': password,
            'line_token': CHANNEL_ACCESS_TOKEN
        }
        response = requests.post(f"{YOUR_COMPUTER_URL}/start", json=data, timeout=10)
        logger.info(f"📤 Sent to local computer: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        logger.error(f"❌ Cannot connect to local computer: {e}")
        return False

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
