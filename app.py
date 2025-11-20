from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import threading
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Lấy thông tin từ environment variables
channel_secret = os.getenv('LINE_CHANNEL_SECRET', 'YOUR_CHANNEL_SECRET')
channel_access_token = os.getenv('LINE_ACCESS_TOKEN', 'YOUR_ACCESS_TOKEN')

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

# Biến toàn cục
user_sessions = {}
bot_instances = {}

class TicketBotManager:
    def __init__(self):
        self.instances = {}
    
    def create_bot_instance(self, user_id):
        """Tạo instance bot mới cho user"""
        from auto_ticket import TicketTestApp
        bot_instance = TicketTestApp()
        self.instances[user_id] = {
            'bot': bot_instance,
            'running': False,
            'thread': None
        }
        return bot_instance
    
    def stop_bot_instance(self, user_id):
        """Dừng bot instance của user"""
        if user_id in self.instances:
            self.instances[user_id]['running'] = False
            if self.instances[user_id]['bot']:
                self.instances[user_id]['bot'].stop_processing()
            del self.instances[user_id]

bot_manager = TicketBotManager()

@app.route("/")
def home():
    return "🤖 Ticket Automation Bot is Running!"

@app.route("/callback", methods=['POST'])
def callback():
    # Xác thực request từ Line
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    logger.info(f"Received request: {body}")
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    
    return 'OK'

def run_automation(user_id, username, password):
    """Chạy automation trong thread riêng"""
    try:
        # Gửi thông báo bắt đầu
        line_bot_api.push_message(user_id, TextSendMessage(
            text="🚀 Đang khởi động automation ticket..."
        ))
        
        # Tạo bot instance
        bot_instance = bot_manager.create_bot_instance(user_id)
        bot_manager.instances[user_id]['running'] = True
        
        # Thực hiện auto login và chạy
        success = bot_instance.auto_login(username, password)
        
        if success:
            line_bot_api.push_message(user_id, TextSendMessage(
                text="✅ Đăng nhập thành công! Đang bắt đầu xử lý ticket..."
            ))
            
            # Chạy automation
            bot_instance.continuous_processing()
            
        else:
            line_bot_api.push_message(user_id, TextSendMessage(
                text="❌ Đăng nhập thất bại! Vui lòng kiểm tra lại username/password"
            ))
            
    except Exception as e:
        logger.error(f"Automation error: {e}")
        line_bot_api.push_message(user_id, TextSendMessage(
            text=f"💥 Lỗi: {str(e)}"
        ))
    finally:
        bot_manager.instances[user_id]['running'] = False

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    message_text = event.message.text.strip()
    
    logger.info(f"Message from {user_id}: {message_text}")
    
    if message_text.lower() == "help":
        # Hiển thị hướng dẫn
        help_text = """
🤖 TICKET AUTOMATION BOT

📝 CÁCH SỬ DỤNG:

1. 🚀 BẮT ĐẦU:
   Gửi: `login username:password`

2. 🛑 DỪNG LẠI:
   Gửi: `stop`

3. 📊 KIỂM TRA:
   Gửi: `status`

🔐 LƯU Ý:
- Thay thế username/password bằng thông tin thực tế
- Bot sẽ tự động xử lý các ticket 1.***
        """
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=help_text))
    
    elif message_text.lower().startswith("login "):
        # Xử lý đăng nhập
        credentials = message_text[6:]  # Bỏ "login "
        if ":" in credentials:
            username, password = credentials.split(":", 1)
            username = username.strip()
            password = password.strip()
            
            # Lưu session
            user_sessions[user_id] = {
                'status': 'processing',
                'username': username,
                'password': password
            }
            
            # Chạy automation trong thread riêng
            thread = threading.Thread(
                target=run_automation,
                args=(user_id, username, password)
            )
            thread.daemon = True
            thread.start()
            
            line_bot_api.reply_message(event.reply_token, TextSendMessage(
                text="✅ Đã nhận thông tin! Đang khởi động automation..."
            ))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(
                text="❌ Sai định dạng! Vui lòng gửi:\n`login username:password`"
            ))
    
    elif message_text.lower() == "stop":
        # Dừng automation
        bot_manager.stop_bot_instance(user_id)
        if user_id in user_sessions:
            del user_sessions[user_id]
        
        line_bot_api.reply_message(event.reply_token, TextSendMessage(
            text="🛑 Đã dừng automation!"
        ))
    
    elif message_text.lower() == "status":
        # Kiểm tra trạng thái
        is_running = user_id in bot_manager.instances and bot_manager.instances[user_id]['running']
        status_text = "🟢 ĐANG CHẠY" if is_running else "🔴 DỪNG"
        
        line_bot_api.reply_message(event.reply_token, TextSendMessage(
            text=f"📊 TRẠNG THÁI: {status_text}"
        ))
    
    else:
        # Hướng dẫn mặc định
        line_bot_api.reply_message(event.reply_token, TextSendMessage(
            text="🤖 Gửi 'help' để xem hướng dẫn sử dụng"
        ))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)