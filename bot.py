import telebot
import time
import requests
import os

TOKEN = os.environ.get("BOT_TOKEN", "8923484574:AAG1oVyFRtdDo9F0w5uqiRWVf7IVMW9QQTE")
bot = telebot.TeleBot(TOKEN)

COOLDOWN = 86400
user_last_used = {}

REGIONS = ["IND", "BR", "SG", "ID", "BD", "PK", "ME", "TH", "VN", "TW", "US", "EU"]

# Multiple APIs - jo chalegi woh use hogi
APIS = [
    "https://freefire-virusteam.vercel.app/like?uid={uid}&region={region}",
    "https://likes-api-tau.vercel.app/like?uid={uid}&server_name={region}",
    "https://aditya-like-api.vercel.app/like?uid={uid}&server_name={region}",
    "https://ff-like-api-kappa.vercel.app/like?uid={uid}&region={region}",
]

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

        region = parts[1].lower()
        uid = parts[2].strip()

        if region.upper() not in REGIONS:
            bot.reply_to(message, f"❌ Galat region!\n\nUse karo: {', '.join([r.lower() for r in REGIONS])}")
            return

        if not uid.isdigit() or len(uid) < 8:
            bot.reply_to(message, "❌ Galat UID. Sirf number daal (8+ digits).")
            return

    except Exception as e:
        bot.reply_to(message, "❌ Error: " + str(e))
        return

    msg = bot.reply_to(message, "🚀 Real likes request bheja ja raha hai...\nMultiple APIs try kar raha hoon...\nWait karo (30-60 sec)...")

    success = False
    last_error = ""

    for api_template in APIS:
        try:
            api_url = api_template.format(uid=uid, region=region)
            response = requests.get(api_url, timeout=20)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    # Different APIs have different response formats
                    likes_given = data.get("LikesGivenByAPI") or data.get("likes_added") or data.get("LikesAdded") or 0
                    player_name = data.get("PlayerNickname") or data.get("Nickname") or data.get("nickname") or "Unknown"
                    likes_before = data.get("LikesbeforeCommand") or data.get("BeforeLikes") or data.get("before") or "N/A"
                    likes_after = data.get("LikesafterCommand") or data.get("AfterLikes") or data.get("after") or "N/A"
                    
                    if likes_given and int(likes_given) > 0:
                        bot.edit_message_text(
                            chat_id=message.chat.id,
                            message_id=msg.message_id,
                            text=f"✅ Success!\n\n"
                                 f"👤 Player: {player_name}\n"
                                 f"🆔 UID: {uid}\n"
                                 f"🌍 Region: {region.upper()}\n\n"
                                 f"❤️ Likes Before: {likes_before}\n"
                                 f"❤️ Likes After: {likes_after}\n"
                                 f"➕ Added: {likes_given}\n\n"
                                 f"📌 Game mein 5-10 min mein update hoga."
                        )
                        user_last_used[user_id] = time.time()
                        success = True
                        break
                except Exception as e:
                    last_error = str(e)
                    continue
        except Exception as e:
            last_error = str(e)
            continue

    if not success:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=msg.message_id,
            text=f"❌ Sabhi APIs down hain abhi.\n\n"
                 f"Free APIs aksar band ho jati hain.\n"
                 f"Thodi der baad ya kal try karo.\n\n"
                 f"Last error: {last_error[:100]}"
        )

print("Bot Started...")
bot.infinity_polling()
