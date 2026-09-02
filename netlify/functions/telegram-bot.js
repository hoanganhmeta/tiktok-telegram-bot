const axios = require('axios');

exports.handler = async (event, context) => {
  try {
    console.log('Event received:', JSON.stringify(event));
    
    // Parse request body
    let body;
    if (typeof event.body === 'string') {
      body = JSON.parse(event.body || '{}');
    } else {
      body = event.body || {};
    }
    
    console.log('Parsed body:', JSON.stringify(body));
    
    // Get TELEGRAM_TOKEN from environment
    const TELEGRAM_TOKEN = process.env.TELEGRAM_TOKEN;
    console.log('Token exists:', !!TELEGRAM_TOKEN);
    
    if (!TELEGRAM_TOKEN) {
      console.error('TELEGRAM_TOKEN not set');
      return {
        statusCode: 500,
        body: JSON.stringify({ error: 'TELEGRAM_TOKEN not set' })
      };
    }

    // Extract message data
    const message = body.message;
    if (!message) {
      console.log('No message in body');
      return {
        statusCode: 200,
        body: JSON.stringify({ ok: true })
      };
    }

    const chatId = message.chat?.id;
    const text = (message.text || '').trim();

    console.log('Chat ID:', chatId);
    console.log('Message text:', text);

    if (!chatId || !text) {
      console.log('Missing chatId or text');
      return {
        statusCode: 200,
        body: JSON.stringify({ ok: true })
      };
    }

    const botAPI = `https://api.telegram.org/bot${TELEGRAM_TOKEN}`;

    // Handle /start command
    if (text === '/start') {
      console.log('Processing /start command');
      const responseText = `👋 Xin chào! Đây là bot lấy thông tin TikTok.

📝 Cách sử dụng:
/tt <username> - Lấy thông tin người dùng TikTok

Ví dụ: /tt cristiano`;

      try {
        const response = await axios.post(`${botAPI}/sendMessage`, {
          chat_id: chatId,
          text: responseText
        });
        console.log('Message sent successfully');
      } catch (err) {
        console.error('Error sending message:', err.message);
      }

      return {
        statusCode: 200,
        body: JSON.stringify({ ok: true })
      };
    }

    // Handle /tt command
    if (text.startsWith('/tt ')) {
      console.log('Processing /tt command');
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
      let waitMsg;
      try {
        const waitResponse = await axios.post(`${botAPI}/sendMessage`, {
          chat_id: chatId,
          text: '⏳ Đang lấy thông tin...'
        });
        waitMsg = waitResponse.data.result;
      } catch (err) {
        console.error('Error sending wait message:', err.message);
      }

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

📊 Thống kê

👥 Người theo dõi: ${stats.followerCount?.toLocaleString('en-US') || 0}
👤 Đang theo dõi: ${stats.followingCount?.toLocaleString('en-US') || 0}
❤️ Lượt thích: ${stats.heartCount?.toLocaleString('en-US') || 0}
🎬 Số video: ${stats.videoCount || 0}`;

          // Delete waiting message
          if (waitMsg) {
            try {
              await axios.post(`${botAPI}/deleteMessage`, {
                chat_id: chatId,
                message_id: waitMsg.message_id
              });
            } catch (e) {
              console.log('Could not delete wait message');
            }
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
              console.log('Photo send failed, trying text');
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

          if (waitMsg) {
            try {
              await axios.post(`${botAPI}/deleteMessage`, {
                chat_id: chatId,
                message_id: waitMsg.message_id
              });
            } catch (e) {
              console.log('Could not delete wait message');
            }
          }
        }
      } catch (error) {
        console.error('Error fetching TikTok:', error.message);

        await axios.post(`${botAPI}/sendMessage`, {
          chat_id: chatId,
          text: `❌ Lỗi: ${error.message}`
        });

        if (waitMsg) {
          try {
            await axios.post(`${botAPI}/deleteMessage`, {
              chat_id: chatId,
              message_id: waitMsg.message_id
            });
          } catch (e) {
            console.log('Could not delete wait message');
          }
        }
      }

      return {
        statusCode: 200,
        body: JSON.stringify({ ok: true })
      };
    }

    // Handle other messages
    console.log('Processing regular message');
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
    console.error('Error details:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ ok: false, error: error.message })
    };
  }
};
