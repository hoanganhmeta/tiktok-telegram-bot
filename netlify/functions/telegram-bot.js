const axios = require('axios');

exports.handler = async (event, context) => {
  try {
    const body = JSON.parse(event.body || '{}');
    
    if (!body || !body.message) {
      return {
        statusCode: 200,
        body: JSON.stringify({ ok: true })
      };
    }

    const TELEGRAM_TOKEN = process.env.TELEGRAM_TOKEN;
    const message = body.message;
    const chatId = message.chat?.id;
    const text = (message.text || '').trim();

    if (!chatId || !text) {
      return {
        statusCode: 200,
        body: JSON.stringify({ ok: true })
      };
    }

    const botAPI = `https://api.telegram.org/bot${TELEGRAM_TOKEN}`;

    // Handle /start command
    if (text === '/start') {
      const responseText = `👋 Xin chào! Đây là bot lấy thông tin TikTok.

📝 Cách sử dụng:
/tt <username> - Lấy thông tin người dùng TikTok

Ví dụ: /tt cristiano`;

      await axios.post(`${botAPI}/sendMessage`, {
        chat_id: chatId,
        text: responseText
      });

      return {
        statusCode: 200,
        body: JSON.stringify({ ok: true })
      };
    }

    // Handle /tt command
    if (text.startsWith('/tt ')) {
      const username = text.replace('/tt ', '').replace('@', '').trim();

      if (!username) {
        await axios.post(`${botAPI}/sendMessage`, {
          chat_id: chatId,
          text: '❌ Vui lòng nhập username!\n\nCách sử dụng: /tt <username>'
        });
        return {
          statusCode: 200,
          body: JSON.stringify({ ok: true })
        };
      }

      // Send waiting message
      const waitMsg = await axios.post(`${botAPI}/sendMessage`, {
        chat_id: chatId,
        text: '⏳ Đang lấy thông tin...'
      });

      try {
        // Fetch TikTok info
        const headers = {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        };

        const tikTokUrl = `https://www.tiktok.com/api/user/detail/?uniqueId=${encodeURIComponent(username)}`;
        const response = await axios.get(tikTokUrl, { headers, timeout: 10000 });

        const data = response.data;
        if (data.userDetail) {
          const user = data.userDetail.user;
          const stats = data.userDetail.stats;

          const bio = user.signature || 'Không có';
          const region = user.region || 'Không rõ';
          const verified = user.verified ? '✅ Có' : '❌ Không';

          const responseText = `👤 Thông tin TikTok

🆔 Username: ${user.uniqueId}
📛 Tên hiển thị: ${user.nickname}
🌍 Khu vực: ${region}
✅ Xác minh: ${verified}
📝 Bio: ${bio}
🔗 BioLink: Không có

📊 Thống kê

👥 Người theo dõi: ${stats.followerCount?.toLocaleString('en-US') || 0}
👤 Đang theo dõi: ${stats.followingCount?.toLocaleString('en-US') || 0}
❤️ Lượt thích: ${stats.heartCount?.toLocaleString('en-US') || 0}
🎬 Số video: ${stats.videoCount || 0}`;

          // Delete waiting message
          try {
            await axios.post(`${botAPI}/deleteMessage`, {
              chat_id: chatId,
              message_id: waitMsg.data.result.message_id
            });
          } catch (e) {
            // Ignore delete errors
          }

          // Send info
          if (user.avatarLarger) {
            try {
              await axios.post(`${botAPI}/sendPhoto`, {
                chat_id: chatId,
                photo: user.avatarLarger,
                caption: responseText
              });
            } catch (e) {
              await axios.post(`${botAPI}/sendMessage`, {
                chat_id: chatId,
                text: responseText
              });
            }
          } else {
            await axios.post(`${botAPI}/sendMessage`, {
              chat_id: chatId,
              text: responseText
            });
          }
        } else {
          await axios.post(`${botAPI}/sendMessage`, {
            chat_id: chatId,
            text: '❌ Không tìm thấy người dùng! Vui lòng kiểm tra lại username.'
          });

          try {
            await axios.post(`${botAPI}/deleteMessage`, {
              chat_id: chatId,
              message_id: waitMsg.data.result.message_id
            });
          } catch (e) {
            // Ignore
          }
        }
      } catch (error) {
        console.error('Error:', error.message);

        await axios.post(`${botAPI}/sendMessage`, {
          chat_id: chatId,
          text: `❌ Lỗi: ${error.message}`
        });

        try {
          await axios.post(`${botAPI}/deleteMessage`, {
            chat_id: chatId,
            message_id: waitMsg.data.result.message_id
          });
        } catch (e) {
          // Ignore
        }
      }

      return {
        statusCode: 200,
        body: JSON.stringify({ ok: true })
      };
    }

    // Handle other messages
    await axios.post(`${botAPI}/sendMessage`, {
      chat_id: chatId,
      text: '💡 Sử dụng /tt <username> để lấy thông tin TikTok\n\nVí dụ: /tt cristiano'
    });

    return {
      statusCode: 200,
      body: JSON.stringify({ ok: true })
    };

  } catch (error) {
    console.error('Error in handler:', error.message);
    return {
      statusCode: 500,
      body: JSON.stringify({ ok: false, error: error.message })
    };
  }
};
