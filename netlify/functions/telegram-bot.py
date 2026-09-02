import json
import logging
from telegram import Bot, Update
import requests
import os
from urllib.parse import quote

# Set up logging
logger = logging.getLogger(__name__)

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


def handler(event, context):
    """Netlify function handler for Telegram webhook"""
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        if not body:
            return {
                'statusCode': 200,
                'body': json.dumps({'ok': True})
            }
        
        # Initialize bot
        bot = Bot(token=TELEGRAM_TOKEN)
        
        # Get message
        message = body.get('message', {})
        chat_id = message.get('chat', {}).get('id')
        text = message.get('text', '').strip()
        
        if not chat_id or not text:
            return {
                'statusCode': 200,
                'body': json.dumps({'ok': True})
            }
        
        # Handle /start command
        if text == '/start':
            response_text = """👋 Xin chào! Đây là bot lấy thông tin TikTok.

📝 Cách sử dụng:
/tt <username> - Lấy thông tin người dùng TikTok

Ví dụ: /tt cristiano"""
            bot.send_message(chat_id=chat_id, text=response_text)
            
        # Handle /tt command
        elif text.startswith('/tt '):
            username = text.replace('/tt ', '').replace('@', '').strip()
            
            if not username:
                bot.send_message(chat_id=chat_id, text="❌ Vui lòng nhập username!\n\nCách sử dụng: /tt <username>")
                return {
                    'statusCode': 200,
                    'body': json.dumps({'ok': True})
                }
            
            # Send waiting message
            wait_msg = bot.send_message(chat_id=chat_id, text="⏳ Đang lấy thông tin...")
            
            try:
                user_info = get_tiktok_user_info(username)
                
                if not user_info:
                    bot.send_message(chat_id=chat_id, text="❌ Không tìm thấy người dùng! Vui lòng kiểm tra lại username.")
                    bot.delete_message(chat_id=chat_id, message_id=wait_msg.message_id)
                    return {
                        'statusCode': 200,
                        'body': json.dumps({'ok': True})
                    }
                
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
                try:
                    bot.delete_message(chat_id=chat_id, message_id=wait_msg.message_id)
                except:
                    pass
                
                # Send info with avatar if available
                if user_info['avatar']:
                    try:
                        bot.send_photo(chat_id=chat_id, photo=user_info['avatar'], caption=response_text)
                    except:
                        bot.send_message(chat_id=chat_id, text=response_text)
                else:
                    bot.send_message(chat_id=chat_id, text=response_text)
                    
            except Exception as e:
                logger.error(f"Error: {str(e)}")
                try:
                    bot.delete_message(chat_id=chat_id, message_id=wait_msg.message_id)
                except:
                    pass
                bot.send_message(chat_id=chat_id, text=f"❌ Lỗi: {str(e)}")
        
        # Handle other messages
        else:
            bot.send_message(chat_id=chat_id, text="💡 Sử dụng /tt <username> để lấy thông tin TikTok\n\nVí dụ: /tt cristiano")
        
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
