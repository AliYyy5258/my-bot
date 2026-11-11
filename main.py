import os, json, telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
bot = telebot.TeleBot(TOKEN)

FILE = "data.json"
if not os.path.exists(FILE):
    with open(FILE, "w") as f:
        json.dump({"arqams": [], "daf3": "طرق الدفع:\nالكريمي: 000000\nام فلوس: 000000"}, f)

def load():
    with open(FILE) as f: return json.load(f)
def save(d):
    with open(FILE, "w") as f: json.dump(d, f)

user_state = {}

def main_kb(is_admin=False):
    m = InlineKeyboardMarkup()
    m.add(InlineKeyboardButton("📱 عرض الارقام", callback_data="show"))
    m.add(InlineKeyboardButton("💳 طرق الدفع", callback_data="pay"))
    m.add(InlineKeyboardButton("🛒 اطلب رقم", callback_data="order"))
    if is_admin:
        m.add(InlineKeyboardButton("➕ اضافة رقم", callback_data="add"))
        m.add(InlineKeyboardButton("🗑 حذف رقم", callback_data="delete"))
        m.add(InlineKeyboardButton("✏️ تعديل طرق الدفع", callback_data="edit_pay"))
    return m

@bot.message_handler(commands=[ start ])
def start(msg):
    is_admin = msg.from_user.id == ADMIN_ID
    bot.send_message(msg.chat.id, "🔥 اهلا في متجر الارقام الجاهزة 🔥\nاختار من الازرار:", reply_markup=main_kb(is_admin))

@bot.callback_query_handler(func=lambda c: True)
def cb(call):
    d = load()
    uid = call.from_user.id
    is_admin = uid == ADMIN_ID
    if call.data == "show":
        if not d["arqams"]:
            txt = "لا يوجد ارقام حاليا"
        else:
            txt = "📱 الارقام المتوفرة:\n\n"
            for i, a in enumerate(d["arqams"], 1):
                txt += f"{i} - {a[ num ]} | {a[ price ]}\n"
        bot.edit_message_text(txt, call.message.chat.id, call.message.message_id, reply_markup=main_kb(is_admin))
    elif call.data == "pay":
        bot.edit_message_text(d["daf3"], call.message.chat.id, call.message.message_id, reply_markup=main_kb(is_admin))
    elif call.data == "order":
        bot.edit_message_text("ارسل رقم الطلب اللي تشتيه", call.message.chat.id, call.message.message_id, reply_markup=main_kb(is_admin))
    elif call.data == "add" and is_admin:
        user_state[uid] = "wait_num"
        bot.send_message(call.message.chat.id, "ارسل الرقم الجديد")
    elif call.data == "delete" and is_admin:
        if not d["arqams"]:
            bot.send_message(call.message.chat.id, "مافي ارقام للحذف")
            return
        txt = "ارسل رقم الترتيب اللي تشتي تحذفه:\n"
        for i, a in enumerate(d["arqams"], 1):
            txt += f"{i} - {a[ num ]}\n"
        user_state[uid] = "wait_del"
        bot.send_message(call.message.chat.id, txt)
    elif call.data == "edit_pay" and is_admin:
        user_state[uid] = "wait_pay"
        bot.send_message(call.message.chat.id, "ارسل طرق الدفع الجديدة")

@bot.message_handler(func=lambda m: True)
def handle(msg):
    uid = msg.from_user.id
    if uid != ADMIN_ID:
        return
    state = user_state.get(uid)
    d = load()
    if state == "wait_num":
        user_state[uid] = ("wait_price", msg.text)
        bot.send_message(msg.chat.id, "تمام ✅ الحين ارسل السعر")
    elif isinstance(state, tuple) and state[0] == "wait_price":
        num = state[1]
        price = msg.text
        d["arqams"].append({"num": num, "price": price})
        save(d)
        user_state.pop(uid, None)
        bot.send_message(msg.chat.id, f"تم اضافة الرقم ✅\n{num} - {price}", reply_markup=main_kb(True))
    elif state == "wait_del":
        try:
            idx = int(msg.text) - 1
            removed = d["arqams"].pop(idx)
            save(d)
            bot.send_message(msg.chat.id, f"تم حذف {removed[ num ]} ✅", reply_markup=main_kb(True))
        except:
            bot.send_message(msg.chat.id, "ارسل رقم صحيح")
        user_state.pop(uid, None)
    elif state == "wait_pay":
        d["daf3"] = msg.text
        save(d)
        user_state.pop(uid, None)
        bot.send_message(msg.chat.id, "تم تعديل طرق الدفع ✅", reply_markup=main_kb(True))

print("البوت شغال...")
bot.polling()
  
