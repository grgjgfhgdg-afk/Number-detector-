import os
import telebot
import requests
from flask import Flask, request
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# المفاتيح الخاصة بك
TELEGRAM_TOKEN = '7895575668:AAFLD_VJA5iPJWL1sCk_djWcm11SqeBHNXQ'
NUMVERIFY_KEY = 'e8f394a1a53023d200f9674f3e82b709'

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = Flask(__name__)

# دالة الترحيب مع زر الدعم الفني
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "مرحباً بك في بوت كاشف الأرقام العالمي! 🔎\n\n"
        "يرجى إرسال الرقم المراد فحصه مع رمز الدولة بدون إشارة (+).\n"
        "مثال: 967770000000\n\n"
        "💬 للتواصل مع الإدارة، اضغط على زر الدعم الفني أدناه."
    )
    
    markup = InlineKeyboardMarkup()
    support_button = InlineKeyboardButton(text="👨‍💻 الدعم الفني", url="h+967783877639")
    markup.add(support_button)
    
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

# استقبال الرقم وفحصه
@bot.message_handler(func=lambda message: True)
def check_number(message):
    phone_number = message.text.strip().replace('+', '')
    
    if not phone_number.isdigit():
        bot.reply_to(message, "❌ خطأ: يرجى إرسال أرقام فقط بدون حروف أو رموز.")
        return

    bot.reply_to(message, "جاري فحص الرقم... ⏳")

    # تعديل الرابط إلى https المشفر والآمن لحل مشكلة الاتصال بالخادم
    api_url = f"https://apilayer.net{NUMVERIFY_KEY}&number={phone_number}"

    try:
        response = requests.get(api_url, timeout=10)
        data = response.json()

        if data.get('valid') == True:
            country = data.get('country_name', 'غير معروف')
            location = data.get('location', 'غير معروف')
            carrier = data.get('carrier', 'غير معروف')
            line_type = data.get('line_type', 'غير معروف')

            result_text = (
                f"✅ **معلومات الرقم المستعلم عنه:**\n\n"
                f"📞 **الرقم:** {phone_number}\n"
                f"🌍 **الدولة:** {country}\n"
                f"📍 **المنطقة:** {location}\n"
                f"📡 **الشبكة (الشركة):** {carrier}\n"
                f"📱 **نوع الخط:** {line_type}"
            )
            bot.reply_to(message, result_text, parse_mode='Markdown')
        else:
            bot.reply_to(message, "❌ لم نتمكن من العثور على بيانات لهذا الرقم، أو أن الرقم غير صحيح.")

    except Exception as e:
        bot.reply_to(message, "⚠️ حدث خطأ أثناء الاتصال بالخادم، يرجى المحاولة لاحقاً.")

# مسارات الويب هوك لاستقبال رسائل تليجرام وتوجيهها للكود
@app.route('/' + TELEGRAM_TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    render_url = os.environ.get("RENDER_EXTERNAL_URL")
    if render_url:
        # تأكيد استخدام الرابط الآمن في الويب هوك أيضاً
        secure_url = render_url.replace("http://", "https://")
        bot.set_webhook(url=secure_url + '/' + TELEGRAM_TOKEN)
        return "تم ربط الويب هوك بنجاح!", 200
    return "سيرفر البوت يعمل، بانتظار إعداد الرابط الخارجي.", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
