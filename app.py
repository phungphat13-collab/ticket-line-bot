from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Lấy thông tin từ environment variables
channel_secret = os.getenv('LINE_CHANNEL_SECRET')
channel_access_token = os.getenv('LINE_ACCESS_TOKEN')

logger.info(f"Channel secret: {channel_secret}")
logger.info(f"Channel access token: {channel_access_token}")

if not channel_secret or not channel_access_token:
    logger.error("❌ MISSING: LINE_CHANNEL_SECRET or LINE_ACCESS_TOKEN")

# Khởi tạo Line Bot
try:
    line_bot_api = LineBotApi(channel_access_token)
    handler = WebhookHandler(channel_secret)
    logger.info("✅ Line Bot initialized successfully")
except Exception as e:
    logger.error(f"❌ Error initializing Line Bot: {e}")

@app.route("/")
def home():
    logger.info("✅ Home page accessed")
    return "🤖 Ticket Bot is running! Use /callback for webhook."

@app.route("/callback", methods=['POST'])
def callback():
    logger.info("✅ Webhook received")
    
    # Get signature header
    signature = request.headers.get('X-Line-Signature', '')
    
    # Get request body as text
    body = request.get_data(as_text=True)
    logger.info(f"Request body: {body}")
    
    # Handle webhook body
    try:
        handler.handle(body, signature)
        logger.info("✅ Webhook handled successfully")
    except InvalidSignatureError:
        logger.error("❌ Invalid signature")
        abort(400)
    except Exception as e:
        logger.error(f"❌ Error handling webhook: {e}")
        abort(500)
    
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        logger.info(f"📨 Message received: {event.message.text}")
        
        # Xử lý các lệnh đơn giản
        if event.message.text.lower() == "help":
            reply_text = "🤖 Ticket Bot Help:\n• help - Hiển thị hướng dẫn\n• status - Kiểm tra trạng thái"
        elif event.message.text.lower() == "status":
            reply_text = "✅ Bot đang hoạt động bình thường!"
        else:
            reply_text = f"Bot nhận được: {event.message.text}"
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )
        logger.info("✅ Reply sent successfully")
        
    except Exception as e:
        logger.error(f"❌ Error replying message: {e}")

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 Starting app on port {port}")
    app.run(host='0.0.0.0', port=port)
