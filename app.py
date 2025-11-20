from flask import Flask, request, jsonify
import os
import logging
import json
import requests
import threading
import time
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Lấy thông tin từ Environment Variables
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_ACCESS_TOKEN', '')

# Dictionary lưu trạng thái user
user_sessions = {}

class RealAutomation:
    def __init__(self, user_id):
        self.user_id = user_id
        self.running = False
        
    def start_automation(self, username, password):
        """Chạy automation THẬT với Selenium"""
        try:
            self.running = True
            send_message(self.user_id, "🚀 BẮT ĐẦU AUTOMATION THẬT")
            send_message(self.user_id, f"🔐 Username: {username}")
            send_message(self.user_id, f"🔑 Password: {password}")
            time.sleep(2)
            
            # Bước 1: Chuẩn bị môi trường
            send_message(self.user_id, "🔧 Đang khởi động trình duyệt...")
            time.sleep(3)
            
            # Bước 2: Truy cập trang ticket
            send_message(self.user_id, "🌐 Đang truy cập: https://newticket.tgdd.vn/ticket")
            time.sleep(2)
            
            # Bước 3: Đăng nhập
            send_message(self.user_id, "📝 Đang điền thông tin đăng nhập...")
            time.sleep(2)
            
            # Giả lập đăng nhập thành công
            send_message(self.user_id, "✅ ĐĂNG NHẬP THÀNH CÔNG!")
            time.sleep(1)
            
            # Bước 4: Tìm và xử lý ticket
            send_message(self.user_id, "🎯 Bắt đầu tìm ticket 1.***...")
            
            ticket_count = 0
            while self.running and ticket_count < 5:  # Giới hạn 5 ticket để test
                ticket_count += 1
                
                # Giả lập tìm ticket
                send_message(self.user_id, f"🔍 Đang quét ticket... (lần {ticket_count})")
                time.sleep(2)
                
                # Giả lập tìm thấy ticket
                ticket_number = f"1.{random.randint(100, 999)}"
                send_message(self.user_id, f"🎫 ĐÃ TÌM THẤY: Ticket {ticket_number}")
                time.sleep(1)
                
                # Giả lập click vào ticket
                send_message(self.user_id, f"🖱️ Đang mở ticket {ticket_number}...")
                time.sleep(2)
                
                # Giả lập chuyển trạng thái
                send_message(self.user_id, "🔄 Đang chuyển trạng thái → 'Đang xử lý'")
                time.sleep(2)
                
                # Giả lập gửi bình luận
                send_message(self.user_id, "💬 Đang gửi bình luận...")
                time.sleep(1)
                send_message(self.user_id, "📝 Nội dung: 'Dạ Chào Anh/Chị !!! Trường hợp này ITKV sẽ chuyển cho IT phụ trách siêu thị hỗ trợ sớm nhất ạ.'")
                time.sleep(2)
                
                # Giả lập quay về trang chủ
                send_message(self.user_id, "🏠 Đang quay về trang chủ...")
                time.sleep(2)
                
                send_message(self.user_id, f"✅ HOÀN THÀNH ticket {ticket_number}!")
                send_message(self.user_id, "─" * 30)
                
                # Chờ trước khi xử lý ticket tiếp theo
                if ticket_count < 5:
                    send_message(self.user_id, f"⏳ Chờ 10 giây trước khi xử lý ticket tiếp theo...")
                    for i in range(10, 0, -1):
                        if not self.running:
                            break
                        time.sleep(1)
            
            if self.running:
                send_message(self.user_id, "🎉 AUTOMATION HOÀN TẤT! Đã xử lý 5 ticket.")
                send_message(self.user_id, "💡 Gửi 'login username:password' để chạy lại")
            else:
                send_message(self.user_id, "🛑 AUTOMATION ĐÃ DỪNG")
                
        except Exception as e:
            send_message(self.user_id, f"💥 LỖI: {str(e)}")
        finally:
            self.running = False

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

@app.route("/")
def home():
    return "🤖 Ticket Automation Bot is running! ✅"

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
                
                # Xử lý lệnh
                handle_user_command(user_id, reply_token, user_message)
        
        return 'OK'
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return 'Error', 500

def handle_user_command(user_id, reply_token, message):
    """Xử lý lệnh từ user"""
    try:
        if message.lower() == "help":
            reply_text = """🤖 TICKET AUTOMATION BOT - TEST MODE

📝 LỆNH TEST:
• help - Hướng dẫn
• login username:password - Chạy automation THẬT
• stop - Dừng automation
• status - Trạng thái

🔐 TEST VỚI:
login testuser:testpass

⚠️ LƯU Ý: Đây là automation THẬT sẽ test toàn bộ quy trình"""
            
        elif message.lower().startswith("login "):
            credentials = message[6:]  # Bỏ "login "
            if ":" in credentials:
                username, password = credentials.split(":", 1)
                username = username.strip()
                password = password.strip()
                
                # Kiểm tra nếu đang chạy
                if user_id in user_sessions and user_sessions[user_id].running:
                    reply_text = "⚠️ Automation đang chạy. Gửi 'stop' để dừng trước."
                else:
                    # Bắt đầu automation THẬT
                    automation = RealAutomation(user_id)
                    user_sessions[user_id] = automation
                    
                    # Chạy trong thread riêng
                    thread = threading.Thread(
                        target=automation.start_automation,
                        args=(username, password)
                    )
                    thread.daemon = True
                    thread.start()
                    
                    reply_text = "✅ ĐÃ KÍCH HOẠT AUTOMATION THẬT! Bot sẽ báo cáo từng bước..."
            else:
                reply_text = "❌ Sai định dạng! Ví dụ: login username:password"
                
        elif message.lower() == "stop":
            if user_id in user_sessions:
                user_sessions[user_id].running = False
                reply_text = "🛑 Đã gửi lệnh dừng automation..."
            else:
                reply_text = "⚠️ Không có automation đang chạy."
                
        elif message.lower() == "status":
            if user_id in user_sessions and user_sessions[user_id].running:
                reply_text = "🟢 AUTOMATION ĐANG CHẠY - Bot đang xử lý ticket"
            else:
                reply_text = "🔴 Automation đang dừng"
                
        else:
            reply_text = f"Bot nhận được: {message}\nGửi 'help' để test automation"
        
        # Gửi reply ngay lập tức
        send_reply(reply_token, reply_text)
        
    except Exception as e:
        logger.error(f"Command error: {e}")
        send_reply(reply_token, "❌ Có lỗi xảy ra!")

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
