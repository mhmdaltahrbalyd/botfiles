import os
import json
import telebot
from telebot import types
from datetime import datetime

# ================== الإعدادات ==================
BOT_TOKEN = "7355512938:AAG00Szn3iuj_207zvypAjcG1Mn7IMyVtOY"
CHANNEL_USERNAME = "@jvdhdudbekebd"          # معرف قناتك
OWNER_ID = 5174813723                    # ضع معرف حسابك (المالك)
POSTS_FILE = "posts.json"
USERS_FILE = "users.json"

bot = telebot.TeleBot(BOT_TOKEN)
bot.remove_webhook()

# ========== إنشاء الملفات إذا لم توجد ==========
if not os.path.exists(POSTS_FILE):
    with open(POSTS_FILE, "w") as f:
        json.dump([], f)

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)

# ========== دوال إدارة المستخدمين ==========
def load_users():
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def register_user(user_id, username=None, first_name=None):
    users = load_users()
    uid_str = str(user_id)
    if uid_str not in users:
        users[uid_str] = {
            "id": user_id,
            "username": username,
            "first_name": first_name,
            "activated": False,
            "interacted": False,
            "received": False,
            "first_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_users(users)

def mark_activated(user_id):
    users = load_users()
    uid = str(user_id)
    if uid in users:
        users[uid]["activated"] = True
        save_users(users)

def mark_interacted(user_id):
    users = load_users()
    uid = str(user_id)
    if uid in users:
        users[uid]["interacted"] = True
        save_users(users)

def mark_received(user_id):
    users = load_users()
    uid = str(user_id)
    if uid in users:
        users[uid]["received"] = True
        save_users(users)

def get_stats():
    users = load_users()
    total = len(users)
    activated = sum(1 for u in users.values() if u.get("activated"))
    interacted = sum(1 for u in users.values() if u.get("interacted"))
    received = sum(1 for u in users.values() if u.get("received"))
    return total, activated, interacted, received

def get_all_user_ids():
    users = load_users()
    return [int(uid) for uid in users.keys()]

# ========== دوال المنشورات ==========
def save_post(post_text):
    with open(POSTS_FILE, "r") as f:
        posts = json.load(f)
    posts.append(post_text)
    with open(POSTS_FILE, "w") as f:
        json.dump(posts, f)

def get_all_posts():
    with open(POSTS_FILE, "r") as f:
        return json.load(f)

# ========== دوال الاشتراك ==========
def is_user_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ========== دالة إنشاء الأزرار بالأرقام ==========
def get_stats_markup():
    _, _, interacted, received = get_stats()
    markup = types.InlineKeyboardMarkup()
    btn_activate = types.InlineKeyboardButton("كليكي هنا باش تفعل البوت 🌚✨", callback_data="activate")
    btn_react = types.InlineKeyboardButton(f"🫀 تفاعل ({interacted})", callback_data="react")
    btn_get = types.InlineKeyboardButton(f"📥 استلام ({received})", callback_data="get_files")
    markup.add(btn_activate)
    markup.add(btn_react)
    markup.add(btn_get)
    return markup

# ========== أوامر الأدمن ==========
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "❌ هذا الأمر للمالك فقط.")
        return
    total, activated, interacted, received = get_stats()
    text = (
        f"👑 **لوحة تحكم الأدمن**\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👥 إجمالي المستخدمين: `{total}`\n"
        f"✅ عدد المُفعَّلين: `{activated}`\n"
        f"🫀 عدد المتفاعلين: `{interacted}`\n"
        f"📥 عدد المستلمين: `{received}`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📊 /users - لعرض قائمة المستخدمين\n"
        f"📢 /broadcast <رسالة> - لإذاعة رسالة للجميع"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['users'])
def list_users(message):
    if message.from_user.id != OWNER_ID:
        return
    users = load_users()
    if not users:
        bot.send_message(message.chat.id, "⚠️ لا يوجد مستخدمون بعد.")
        return
    text = "📋 **قائمة المستخدمين:**\n\n"
    for uid, data in users.items():
        name = data.get("first_name") or data.get("username") or "بدون اسم"
        text += f"• {name} – `{uid}`\n"
    bot.send_message(message.chat.id, text[:4000], parse_mode="Markdown")

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.from_user.id != OWNER_ID:
        return
    cmd_parts = message.text.split(maxsplit=1)
    if len(cmd_parts) < 2:
        bot.reply_to(message, "⚠️ الصيغة: /broadcast النص")
        return
    broadcast_msg = cmd_parts[1]
    user_ids = get_all_user_ids()
    success = 0
    fail = 0
    for uid in user_ids:
        try:
            bot.send_message(uid, f"📢 **إذاعة من الأدمن:**\n\n{broadcast_msg}", parse_mode="Markdown")
            success += 1
        except:
            fail += 1
    bot.reply_to(message, f"✅ تم الإرسال لـ {success} مستخدم.\n❌ فشل لـ {fail}.")

# ========== أمر بدء تسجيل المستخدم ==========
@bot.message_handler(commands=['start'])
def start_cmd(message):
    user = message.from_user
    register_user(user.id, user.username, user.first_name)
    bot.reply_to(message, "✅ مرحباً! تم تسجيلك. استخدم البوت عبر القناة.")

# ========== أمر إضافة منشور (للمالك فقط) ==========
@bot.message_handler(commands=['addpost'])
def add_post_command(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "❌ هذا الأمر للمالك فقط.")
        return
    if message.chat.type != "private":
        return
    msg = bot.send_message(message.chat.id, "📝 أرسل الآن نص المنشور (الكونفيج):")
    bot.register_next_step_handler(msg, save_new_post)

def save_new_post(message):
    save_post(message.text)
    bot.send_message(message.chat.id, "✅ تم حفظ المنشور!")

# ========== أمر نشر القائمة في القناة ==========
@bot.message_handler(commands=['publish'])
def publish_to_channel(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "❌ هذا الأمر للمالك فقط.")
        return
    if message.chat.type != "private":
        return
    posts = get_all_posts()
    if not posts:
        bot.send_message(message.chat.id, "⚠️ لا توجد منشورات محفوظة.")
        return
    text = (
        f"📡 **تم إضافة {len(posts)} ملف كونفيج جديد**\n"
        f"✨ **جميع الملفات ذات جودة عالية وجاهزة للاستخدام**\n\n"
        f"🔽 قم بالخطوات التالية:\n"
        f"1️⃣ اضغط على زر التفعيل\n"
        f"2️⃣ ثم زر التفاعل\n"
        f"3️⃣ ثم زر استلام الملفات"
    )
    markup = get_stats_markup()
    bot.send_message(CHANNEL_USERNAME, text, reply_markup=markup, parse_mode="Markdown")

# ========== معالجة الأزرار ==========
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    uid = call.from_user.id
    register_user(uid, call.from_user.username, call.from_user.first_name)

    if call.data == "activate":
        mark_activated(uid)
        bot.answer_callback_query(call.id, "✅ تم تفعيل البوت! يمكنك الآن التفاعل (🫀✨).")
        # تحديث الأزرار (إعادة إرسال نفس الرسالة مع الأزرار المحدثة)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=get_stats_markup())

    elif call.data == "react":
        user_data = load_users().get(str(uid), {})
        if not user_data.get("activated"):
            bot.answer_callback_query(call.id, "❌ يجب أن تفعل البوت أولاً (اضغط على الزر الأول)!", show_alert=True)
            return
        if not is_user_subscribed(uid):
            bot.answer_callback_query(call.id, "❌ اشترك في القناة أولاً!", show_alert=True)
            return
        if user_data.get("interacted"):
            bot.answer_callback_query(call.id, "⚠️ لقد قمت بالتفاعل بالفعل!", show_alert=True)
            return
        mark_interacted(uid)
        bot.answer_callback_query(call.id, "✅ تم التفاعل! يمكنك الآن استلام الملفات.")
        # تحديث الأزرار (زيادة عدد المتفاعلين)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=get_stats_markup())

    elif call.data == "get_files":
        user_data = load_users().get(str(uid), {})
        if not user_data.get("activated"):
            bot.answer_callback_query(call.id, "❌ يجب أن تفعل البوت أولاً (اضغط على الزر الأول)!", show_alert=True)
            return
        if not user_data.get("interacted"):
            bot.answer_callback_query(call.id, "❌ يجب أن تتفاعل أولاً (اضغط على 🫀✨)!", show_alert=True)
            return
        if user_data.get("received"):
            bot.answer_callback_query(call.id, "⚠️ لقد استلمت الملفات بالفعل!", show_alert=True)
            return
        if not is_user_subscribed(uid):
            bot.answer_callback_query(call.id, "❌ اشترك في القناة أولاً!", show_alert=True)
            return
        posts = get_all_posts()
        if not posts:
            bot.send_message(uid, "⚠️ لا توجد ملفات حالياً.")
            return
        for idx, p in enumerate(posts, 1):
            bot.send_message(uid, f"📄 **كونفيج {idx}**\n```\n{p}\n```", parse_mode="Markdown")
        mark_received(uid)
        # تحديث الأزرار (زيادة عدد المستلمين)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=get_stats_markup())
        bot.send_message(uid, "♣❀ **المطور طاتي يقول لك شكراً على الزيارة** ♣❀")

# ========== تشغيل البوت ==========
if __name__ == "__main__":
    print("✅ البوت يعمل...")
    bot.polling(none_stop=True, interval=0)
