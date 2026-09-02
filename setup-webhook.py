#!/usr/bin/env python3
"""
Script to setup Telegram webhook on Netlify
Run this script after deploying to Netlify
"""

import requests
import sys

def setup_webhook(token, webhook_url):
    """Setup Telegram webhook"""
    try:
        url = f"https://api.telegram.org/bot{token}/setWebhook"
        
        data = {
            'url': webhook_url,
            'allowed_updates': ['message', 'callback_query']
        }
        
        response = requests.post(url, json=data)
        result = response.json()
        
        if result['ok']:
            print("✅ Webhook setup successfully!")
            print(f"Webhook URL: {webhook_url}")
            return True
        else:
            print(f"❌ Error: {result.get('description', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python setup-webhook.py <token> <webhook_url>")
        print("\nExample:")
        print("python setup-webhook.py 123456:ABC-DEF https://your-site.netlify.app/.netlify/functions/telegram-bot")
        sys.exit(1)
    
    token = sys.argv[1]
    webhook_url = sys.argv[2]
    
    setup_webhook(token, webhook_url)
