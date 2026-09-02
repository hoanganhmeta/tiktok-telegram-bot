import json
import logging
from telegram import Update, ParseMode
from telegram.ext import Dispatcher, MessageHandler, CommandHandler, Filters
from telegram.error import TelegramError
import requests
import os
from urllib.parse import quote

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Get environment variables
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')

def get_tiktok_user_info(username):
    """
    Fetch TikTok user information
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Using unofficial API
        url = f"https://www.tiktok.com/api/user/detail/?uniqueId={quote(username)}"
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'userDetail' in data:
                user = data['userDetail']['user']
                stats = data['userDetail']['stats']
                
                user_info = {
                    'username': user.get('uniqueId', 'N/A'),
                    'nickname': user.get('nickname', 'N/A'),
                    'avatar': user.get('avatarLarger', ''),
                    'signature': user.get('signature', ''),
                    'region': user.get('region', 'Không rõ'),
                    'verified': user.get('verified', False),
                    'follower_count': stats.get('followerCount', 0),
                    'following_count': stats.get('followingCount', 0),
                    'heart_count': stats.get('heartCount', 0),
                    'video_count': stats.get('videoCount', 0),
                }
                return user_info
        
        return None
        
    except Exception as e:
        logger.error(f"Error fetching TikTok info: {str(e)}")
        return None


def start(update, context):
    """Start command"""
    message = """👋 Xin chào! Đây là bot lấy thông tin TikTok.

📝 Cách sử dụng:
/tt <username> - Lấy thông tin người dùng TikTok

Ví dụ: /tt truccphuongg07"""
    
    update.message.reply_text(message)


def handle_tt_command(update, context):
    """Handle /tt command"""
    if not context.args:
        update.message.reply_text("❌ Vui lòng nhập username!\n\nCách sử dụng: /tt <username>")
        return
    
    username = context.args[0].replace('@', '')
    
    # Send waiting message
    wait_msg = update.message.reply_text("⏳ Đang lấy thông tin...")
    
    try:
        user_info = get_tiktok_user_info(username)
        
        if not user_info:
            update.message.reply_text("❌ Không tìm thấy người dùng! Vui lòng kiểm tra lại username.")
            wait_msg.delete()
            return
        
        # Format response
        bio = user_info['signature'] if user_info['signature'] else "Không có"
        region = user_info['region'] if user_info['region'] else "Không rõ"
        verified = "✅ Có" if user_info['verified'] else "❌ Không"
        
        response_text = f"""👤 Thông tin TikTok

🆔 Username: {user_info['username']}
📛 Tên hiển thị: {user_info['nickname']}
🌍 Khu vực: {region}
✅ Xác minh: {verified}
📝 Bio: {bio}
🔗 BioLink: Không có

📊 Thống kê

👥 Người theo dõi: {user_info['follower_count']:,}
👤 Đang theo dõi: {user_info['following_count']:,}
❤️ Lượt thích: {user_info['heart_count']:,}
🎬 Số video: {user_info['video_count']}"""
        
        # Delete waiting message
        wait_msg.delete()
        
        # Send info with avatar if available
        if user_info['avatar']:
            try:
                update.message.reply_photo(
                    photo=user_info['avatar'],
                    caption=response_text,
                    parse_mode=ParseMode.HTML
                )
            except:
                update.message.reply_text(response_text, parse_mode=ParseMode.HTML)
        else:
            update.message.reply_text(response_text, parse_mode=ParseMode.HTML)
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        wait_msg.delete()
        update.message.reply_text(f"❌ Lỗi: {str(e)}")


def handle_message(update, context):
    """Handle other messages"""
    update.message.reply_text("💡 Sử dụng /tt <username> để lấy thông tin TikTok\n\nVí dụ: /tt cristiano")


def setup_dispatcher():
    """Setup command and message handlers"""
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('tt', handle_tt_command))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))


def handler(event, context):
    """Netlify function handler"""
    try:
        body = json.loads(event.get('body', '{}'))
        
        # Setup dispatcher only once
        if not dispatcher.handlers:
            setup_dispatcher()
        
        # Create update object
        update = Update.de_json(body, None)
        
        if update:
            # Process update
            dispatcher.process_update(update)
        
        return {
            'statusCode': 200,
            'body': json.dumps({'ok': True})
        }
        
    except Exception as e:
        logger.error(f"Error in handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'ok': False, 'error': str(e)})
        }
