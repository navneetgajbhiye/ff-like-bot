import telebot
import time
import requests
import os

TOKEN = os.environ.get("BOT_TOKEN", "8923484574:AAG1oVyFRtdDo9F0w5uqiRWVf7IVMW9QQTE")
bot = telebot.TeleBot(TOKEN)

COOLDOWN = 86400
user_last_used = {}

REGIONS = ["IND", "BR", "SG", "ID", "BD", "PK", "ME", "TH", "VN", "TW", "US", "EU"]

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message,
        "👋 Welcome to Free Fire Likes Bot\n\n"
        "• Real likes ke liye /like use karo\n"
        "• Format: /like <region> <uid>\n"
        "• Example: /like ind 123456789\n\n"
        "📍 Available Regions:\n"
        "ind, br, sg, id, bd, pk, me, th, vn, tw, us, eu\n\n"
        "⚠️ Har UID pe 24 ghante mein 1 baar")

@bot.message_handler(commands=['like'])
def get_like(message):
    user_id = message.from_user.id

    if user_id in user_last_used:
        last_time = user_last_used[user_id]
        if time.time() - last_time < COOLDOWN:
            remaining = int((last_time + COOLDOWN - time.time()) / 3600)
            bot.reply_to(message, f"⏳ Cooldown chal raha hai.\n{remaining+1} ghante baad try karo.")
            return

    try:
        parts = message.text.split()
        if len(parts) != 3:
            bot.reply_to(message, "❌ Galat format!\n\nUse karo:\n/like <region> <uid>\n\nExample:\n/like ind 123456789")
            return

        region = parts[1].upper()
        uid = parts[2].strip()

        if region not in REGIONS:
            bot.reply_to(message, f"❌ Galat region!\n\nUse karo: {', '.join([r.lower() for r in REGIONS])}")
            return

        if not uid.isdigit() or len(uid) < 8:
            bot.reply_to(message, "❌ Galat UID. Sirf number daal (8+ digits).")
            return

    except Exception as e:
        bot.reply_to(message, "❌ Error: " + str(e))
        return

    msg = bot.reply_to(message, "🚀 Real likes request bheja ja raha hai...\nWait karo (10-20 sec)...")

    try:
        api_url = f"https://like.nrobotz.com/like?uid={uid}&server={region.lower()}"
        response = requests.get(api_url, timeout=30)
        data = response.json()

        if response.status_code == 200 and data.get("status") == 1:
            likes_before = data.get("LikesbeforeCommand", "N/A")
            likes_after = data.get("LikesafterCommand", "N/A")
            likes_given = data.get("LikesGivenByAPI", 0)
            player_name = data.get("PlayerNickname", "Unknown")

            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=msg.message_id,
                text=f"✅ Success!\n\n"
                     f"👤 Player: {player_name}\n"
                     f"🆔 UID: {uid}\n"
                     f"🌍 Region: {region}\n\n"
                     f"❤️ Likes Before: {likes_before}\n"
                     f"❤️ Likes After: {likes_after}\n"
                     f"➕ Added: {likes_given}\n\n"
                     f"📌 Game mein 5-10 min mein update hoga."
            )
            user_last_used[user_id] = time.time()

        elif data.get("status") == 2:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=msg.message_id,
                text="⚠️ Maximum likes already reached!\nIs UID ko aaj already likes mil chuke hain.\nKal try karo."
            )
        else:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=msg.message_id,
                text=f"❌ Failed!\nResponse: {data}\n\nThodi der baad try karo."
            )

    except Exception as e:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=msg.message_id,
            text=f"❌ Error: {str(e)}\n\nAPI down ho sakti hai."
        )

print("Bot Started...")
bot.infinity_polling()
