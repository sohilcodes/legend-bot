import telebot
import time
import json
import requests
import threading
import os
import pytz
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ============ CONFIG ============
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 6411315434
INVITE_LINK = "https://www.dmwin1.com/#/register?invitationCode=112542087887"
DB_FILE = "users.json"
CLICKS_FILE = "clicks.json"
API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json?ts="

# 🎯 STICKERS
WIN_STICKER_1 = "CAACAgUAAxkBAAFDlppppT351aarhWh_TG_tUy7uko-n6QACZRYAAqYtOVXs-2XdGTALsDoE"
WIN_STICKER_2 = "CAACAgUAAxkBAAFDlpxppT4FFNkF13KJ8AuYgZD4z7HWpAACWhoAAiWkMFXi4IKHogJcszoE"
LOSS_STICKER = "CAACAgUAAxkBAAFDlqJppT4bXj3NuDu4BZ6pSSVG_N8qcgACHhoAAsCAWFdNIjQkeNqKlzoE"

bot = telebot.TeleBot(BOT_TOKEN)  # NO markdown (stable)

# ========= GLOBAL =========
pending_ids = {}
user_stage = {}
signals_enabled = True
last_finished_period = None
predictions = {}
wins = 0
losses = 0
total_signals = 0

# ========= FILE HELPERS =========
def load_json(file, default):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return default

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

users = load_json(DB_FILE, [])
clicks_data = load_json(CLICKS_FILE, {})

def save_user(user):
    if user.id not in users:
        users.append(user.id)
        save_json(DB_FILE, users)

def track_click(user_id):
    uid = str(user_id)
    clicks_data[uid] = clicks_data.get(uid, 0) + 1
    save_json(CLICKS_FILE, clicks_data)

def get_vip_users():
    return [uid for uid, stage in user_stage.items() if stage == 2]

def signal_markup():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🔗 Register on DM Win", url=INVITE_LINK))
    return kb

# ========= FULL FUNNEL START =========
@bot.message_handler(commands=['start'])
def start_cmd(message):
    save_user(message.from_user)
    name = message.from_user.first_name or "Trader"

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🔗 Register on DM Win", callback_data="register"))

    text = f"""👋🏻 Hello {name} Welcome Back!

🚀 Get full access to unlimited premium trading signals.

🏆 For every 10 trades, win 8 to 9 trades on average.

📌 Step 1: Create your DM Win account:
Click the button below to register 👇

📌 Step 2: After signing up, send your 7-digit DM Win User ID here to verify.

⚠️ Without registration & verification, VIP signals will NOT unlock.

💎 Features:
• Advance AI Signals
• Live Predictions
• Win/Loss Tracking
• Premium Accuracy"""

    bot.send_message(message.chat.id, text, reply_markup=kb)

# ========= REGISTER =========
@bot.callback_query_handler(func=lambda c: c.data == "register")
def reg_click(call):
    track_click(call.from_user.id)
    bot.send_message(call.from_user.id, f"🔗 Official Register Link:\n{INVITE_LINK}")

# ========= ID SUBMIT =========
@bot.message_handler(func=lambda m: m.text and m.text.isdigit() and len(m.text) == 7)
def id_submit(message):
    uid = message.from_user.id
    pending_ids[uid] = message.text

    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("✅ Approve", callback_data=f"approve_{uid}"),
        InlineKeyboardButton("❌ Reject", callback_data=f"reject_{uid}")
    )

    bot.send_message(ADMIN_ID, f"📩 New DM Win ID\nUser: {uid}\nID: {message.text}", reply_markup=kb)
    bot.send_message(uid, "⏳ Your ID is under review.")

# ========= APPROVAL =========
@bot.callback_query_handler(func=lambda c: c.data.startswith(("approve_","reject_")))
def approve_user(call):
    if call.from_user.id != ADMIN_ID:
        return

    action, uid = call.data.split("_")
    uid = int(uid)

    if action == "approve":
        user_stage[uid] = 2
        bot.send_message(uid, "✅ VIP Activated!\n🎯 Signals Started Automatically.")
    else:
        bot.send_message(uid, "❌ Invalid ID.")

# ========= ADMIN PANEL =========
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return

    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📊 Stats", callback_data="stats"),
        InlineKeyboardButton("👥 Users", callback_data="users"),
        InlineKeyboardButton("🔗 Click Stats", callback_data="clicks"),
        InlineKeyboardButton("▶️ Start Signals", callback_data="start_sig"),
        InlineKeyboardButton("⛔ Stop Signals", callback_data="stop_sig"),
    )

    bot.send_message(message.chat.id, "👑 ADMIN PANEL", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data in ["stats","users","clicks","start_sig","stop_sig"])
def admin_buttons(call):
    global signals_enabled

    if call.from_user.id != ADMIN_ID:
        return

    if call.data == "stats":
        bot.send_message(ADMIN_ID, f"Signals: {total_signals}\nWins: {wins}\nLoss: {losses}")

    elif call.data == "users":
        bot.send_message(ADMIN_ID, f"Total Users: {len(users)}\nVIP Users: {len(get_vip_users())}")

    elif call.data == "clicks":
        total_clicks = sum(clicks_data.values())
        bot.send_message(ADMIN_ID, f"Total Clicks: {total_clicks}")

    elif call.data == "start_sig":
        signals_enabled = True
        bot.send_message(ADMIN_ID, "Signals Started")

    elif call.data == "stop_sig":
        signals_enabled = False
        bot.send_message(ADMIN_ID, "Signals Stopped")

# ========= SIGNAL SYSTEM =========
def get_api():
    try:
        url = API_URL + str(int(time.time()*1000))
        return requests.get(url, timeout=10).json()
    except:
        return None

def number_to_bs(n):
    return "BIG" if int(n) >= 5 else "SMALL"

def ai_predict(history):
    results = []
    for item in history[:10]:
        num = int(item.get("number", 0))
        results.append("BIG" if num >= 5 else "SMALL")
    return "BIG" if results.count("BIG") > results.count("SMALL") else "SMALL"

def signal_loop():
    global last_finished_period, wins, losses, total_signals

    while True:
        if not signals_enabled:
            time.sleep(2)
            continue

        data = get_api()
        if not data:
            time.sleep(2)
            continue

        history = data["data"]["list"]
        latest = history[0]
        finished = latest["issueNumber"]
        number = latest["number"]
        vip_users = get_vip_users()

        # RESULT CHECK
        if finished in predictions:
            pred = predictions.pop(finished)
            actual = number_to_bs(number)
            total_signals += 1

            if pred == actual:
                wins += 1
                for uid in vip_users:
                    bot.send_message(uid,
                        f"🏆 WIN RESULT\n\nPeriod: {finished}\nPrediction: {pred}\nResult: {actual}",
                        reply_markup=signal_markup())
                    bot.send_sticker(uid, WIN_STICKER_1)
                    bot.send_sticker(uid, WIN_STICKER_2)
            else:
                losses += 1
                for uid in vip_users:
                    bot.send_message(uid,
                        f"❌ LOSS RESULT\n\nPeriod: {finished}\nPrediction: {pred}\nResult: {actual}",
                        reply_markup=signal_markup())
                    bot.send_sticker(uid, LOSS_STICKER)

        # NEW SIGNAL
        if finished and finished != last_finished_period:
            last_finished_period = finished
            next_period = str(int(finished) + 1)
            signal = ai_predict(history)
            predictions[next_period] = signal

            for uid in vip_users:
                bot.send_message(uid,
                    f"🎯 VIP LIVE SIGNAL\n\nNext Period: {next_period}\nPrediction: {signal}",
                    reply_markup=signal_markup())

        time.sleep(2)

threading.Thread(target=signal_loop, daemon=True).start()
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

print("🚀 FULL FINAL WORKING BOT RUNNING")
threading.Thread(target=run_web).start()

bot.infinity_polling(skip_pending=True)
  
