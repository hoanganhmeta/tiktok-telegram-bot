# TikTok Telegram Bot - Chạy trên Netlify

Bot Telegram để lấy thông tin người dùng TikTok. Triển khai trên Netlify bằng Serverless Functions.

## 📋 Tính năng

- ✅ Lấy thông tin user TikTok (follower, following, like, video count)
- ✅ Hiển thị avatar người dùng
- ✅ Định dạng đẹp với emoji
- ✅ Chạy trên Netlify (miễn phí)
- ✅ Webhook support

## 🚀 Cách triển khai

### 1. Tạo Telegram Bot

1. Mở Telegram, tìm `@BotFather`
2. Gửi lệnh `/newbot`
3. Đặt tên và username cho bot
4. Lưu lại **Token** (ví dụ: `123456789:ABCDEFGHIJKLMNOP...`)

### 2. Fork/Clone Repository

```bash
git clone https://github.com/hoanganhmeta/tiktok-telegram-bot.git
cd tiktok-telegram-bot
```

### 3. Triển khai trên Netlify

**Cách A: GitHub Integration (Recommended)**

1. Truy cập [Netlify](https://netlify.com)
2. Đăng nhập bằng GitHub
3. Chọn "New site from Git"
4. Chọn repository `tiktok-telegram-bot`
5. Cấu hình Build:
   - Build command: `pip install -r requirements.txt`
   - Functions directory: `netlify/functions`
   - Publish directory: `public`
6. Thêm Environment Variables:
   - Key: `TELEGRAM_TOKEN`
   - Value: Token từ BotFather
7. Nhấn "Deploy site"

**Cách B: Manual Deploy**

```bash
# Cài đặt Netlify CLI
npm install -g netlify-cli

# Đăng nhập
netlify login

# Triển khai
netlify deploy --prod
```

### 4. Setup Webhook

Sau khi triển khai, bạn sẽ có URL:
```
https://your-site.netlify.app/.netlify/functions/telegram-bot
```

**Chạy script setup:**

```bash
pip install requests
python setup-webhook.py YOUR_BOT_TOKEN https://your-site.netlify.app/.netlify/functions/telegram-bot
```

**Hoặc dùng curl:**

```bash
curl -X POST \
  https://api.telegram.org/botYOUR_BOT_TOKEN/setWebhook \
  -H 'Content-Type: application/json' \
  -d '{
    "url": "https://your-site.netlify.app/.netlify/functions/telegram-bot"
  }'
```

### 5. Test Bot

1. Mở Telegram, tìm bot của bạn
2. Gửi `/start` để kiểm tra
3. Sử dụng: `/tt username`

## 📝 Cách sử dụng

```
/start - Hiển thị hướng dẫn
/tt <username> - Lấy thông tin TikTok user
```

**Ví dụ:**
```
/tt ongg07
/tt @cristiano
/tt tiktok
```

## 📤 Output Format

```
👤 Thông tin TikTok

🆔 Username: ongg07
📛 Tên hiển thị: ♡
🌍 Khu vực: Không rõ
✅ Xác minh: Không
📝 Bio: [Bio của người dùng]
🔗 BioLink: Không có

📊 Thống kê

👥 Người theo dõi: 473
👤 Đang theo dõi: 40
❤️ Lượt thích: 182
🎬 Số video: 3
```

Kèm theo ảnh avatar của người dùng.

## 🔧 Cấu hình

### Environment Variables

Thêm trên Netlify:
```
TELEGRAM_TOKEN=your_bot_token_here
```

### Tuỳ chỉnh

Sửa file `netlify/functions/telegram-bot.py`:

```python
# Thay đổi message format
response_text = f"""👤 Thông tin TikTok
..."""

# Thay đổi API endpoint
url = f"https://api.tiktok.com/..."
```

## 🐛 Troubleshooting

### Webhook không hoạt động

```bash
# Kiểm tra status
curl https://api.telegram.org/botYOUR_TOKEN/getWebhookInfo
```

### Bot không trả lời

1. Kiểm tra Netlify Functions logs
2. Kiểm tra TELEGRAM_TOKEN có đúng không
3. Reset webhook:

```bash
curl -X POST https://api.telegram.org/botYOUR_TOKEN/deleteWebhook
```

Rồi setup lại.

### Lấy thông tin TikTok bị lỗi

- TikTok có thể chặn requests
- Kiểm tra internet connection
- Thử username khác

## 📦 Dependencies

```
python-telegram-bot==13.15
requests==2.31.0
aiohttp==3.9.1
```

## 💾 Project Structure

```
.
├── netlify/
│   └── functions/
│       └── telegram-bot.py      # Main bot code
├── netlify.toml                  # Netlify config
├── requirements.txt              # Python dependencies
├── setup-webhook.py             # Webhook setup script
└── README.md                     # This file
```

## 📊 Performance

- **Cold start**: ~2-3 giây (lần đầu)
- **Response time**: ~1-2 giây
- **Uptime**: 99.9% (Netlify)

## 🔐 Security

- Token được lưu trữ an toàn trong Netlify Environment Variables
- Không log token vào console
- Sử dụng HTTPS cho webhook

## 📚 Tài liệu

- [Telegram Bot API](https://core.telegram.org/bots/api)
- [python-telegram-bot](https://python-telegram-bot.readthedocs.io/)
- [Netlify Functions](https://docs.netlify.com/functions/overview/)

## 🤝 Hỗ trợ

Gặp vấn đề? Tạo issue trên GitHub hoặc liên hệ.

## 📄 License

MIT License

---

**Tạo bởi**: hoanganhmeta  
**Cập nhật lần cuối**: 2024
