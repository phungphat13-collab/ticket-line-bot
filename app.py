from flask import Flask, request, jsonify
import os
import logging
import json
import requests
import threading
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Lấy thông tin từ Environment Variables
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_ACCESS_TOKEN', '')

# Dictionary lưu trạng thái user
user_sessions = {}

class TicketAutomation:
    def __init__(self, user_id):
        self.user_id = user_id
        self.driver = None
        self.running = False
        
    def start_automation(self, username, password):
        """Chạy automation trong thread riêng"""
        try:
            self.running = True
            send_message(self.user_id, "🚀 Đang khởi động automation ticket...")
            
            # Khởi tạo Chrome driver
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Chạy ngầm
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.get("https://newticket.tgdd.vn/ticket")
            
            # Đăng nhập
            if self.auto_login(username, password):
                send_message(self.user_id, "✅ Đăng nhập thành công! Đang xử lý ticket...")
                self.process_tickets()
            else:
                send_message(self.user_id, "❌ Đăng nhập thất bại! Kiểm tra lại username/password")
                
        except Exception as e:
            send_message(self.user_id, f"💥 Lỗi: {str(e)}")
        finally:
            if self.driver:
                self.driver.quit()
            self.running = False
    
    def auto_login(self, username, password):
        """Tự động đăng nhập"""
        try:
            # Tìm và điền form đăng nhập
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_field = self.driver.find_element(By.NAME, "password")
            
            username_field.send_keys(username)
            password_field.send_keys(password)
            
            # Click nút đăng nhập
            login_btn = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_btn.click()
            
            # Chờ đăng nhập thành công
            time.sleep(5)
            return "login" not in self.driver.current_url
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False
    
    def process_tickets(self):
        """Xử lý ticket tự động"""
        try:
            while self.running:
                # Tìm và click ticket 1.***
                ticket_found = self.find_and_click_ticket()
                
                if ticket_found:
                    # Chuyển trạng thái sang "Đang xử lý"
                    self.click_processing_status()
                    
                    # Gửi bình luận
                    self.send_comment("Dạ Chào Anh/Chị !!! Trường hợp này ITKV sẽ chuyển cho IT phụ trách siêu thị hỗ trợ sớm nhất ạ.")
                    
                    send_message(self.user_id, "✅ Đã xử lý 1 ticket!")
                    
                    # Quay về trang chủ
                    self.go_to_home_page()
                
                # Chờ 30 giây trước khi xử lý ticket tiếp theo
                for i in range(30):
                    if not self.running:
                        break
                    time.sleep(1)
                    
        except Exception as e:
            send_message(self.user_id, f"💥 Lỗi xử lý ticket: {str(e)}")
    
    def find_and_click_ticket(self):
        """Tìm và click ticket 1.***"""
        try:
            tickets = self.driver.find_elements(By.XPATH, "//*[starts-with(text(), '1.')]")
            for ticket in tickets:
                if ticket.is_displayed() and not any(x in ticket.text for x in ['10.', '11.', '12.']):
                    ticket.click()
                    time.sleep(3)
                    return True
            return False
        except:
            return False
    
    def click_processing_status(self):
        """Click nút Đang xử lý"""
        try:
            processing_btn = self.driver.find_element(By.XPATH, "//button[contains(., 'Đang xử lý')]")
            processing_btn.click()
            time.sleep(2)
            return True
        except:
            return False
    
    def send_comment(self, comment):
        """Gửi bình luận"""
        try:
            comment_box = self.driver.find_element(By.XPATH, "//textarea")
            comment_box.send_keys(comment)
            
            send_btn = self.driver.find_element(By.XPATH, "//button[contains(., 'Gửi')]")
            send_btn.click()
            time.sleep(2)
            return True
        except:
            return False
    
    def go_to_home_page(self):
        """Về trang chủ"""
        try:
            home_btn = self.driver.find_element(By.XPATH, "//a[contains(., 'Trang chủ')]")
            home_btn.click()
            time.sleep(3)
            return True
        except:
            return False

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
            reply_text = """🤖 TICKET AUTOMATION BOT

📝 LỆNH SỬ DỤNG:
• help - Hiển thị hướng dẫn
• login username:password - Bắt đầu automation
• stop - Dừng automation
• status - Kiểm tra trạng thái

🔐 Ví dụ: login myuser:mypassword"""
            
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
                    # Bắt đầu automation
                    automation = TicketAutomation(user_id)
                    user_sessions[user_id] = automation
                    
                    # Chạy trong thread riêng
                    thread = threading.Thread(
                        target=automation.start_automation,
                        args=(username, password)
                    )
                    thread.daemon = True
                    thread.start()
                    
                    reply_text = "✅ Đã nhận thông tin! Đang khởi động automation..."
            else:
                reply_text = "❌ Sai định dạng! Ví dụ: login username:password"
                
        elif message.lower() == "stop":
            if user_id in user_sessions:
                user_sessions[user_id].running = False
                reply_text = "🛑 Đã dừng automation!"
            else:
                reply_text = "⚠️ Không có automation đang chạy."
                
        elif message.lower() == "status":
            if user_id in user_sessions and user_sessions[user_id].running:
                reply_text = "🟢 Automation đang chạy..."
            else:
                reply_text = "🔴 Automation đang dừng"
                
        else:
            reply_text = f"Bot nhận được: {message}\nGửi 'help' để xem hướng dẫn"
        
        # Gửi reply
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
