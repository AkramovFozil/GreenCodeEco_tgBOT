# main.py
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from config import TOKEN, CHANNELS
from lang import languages

# Logging sozlamalari
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Statistik ma'lumotlar
stats = {"totalMessages": 0, "totalErrors": 0}
userLanguage = {}


# Obunani tekshirish
async def check_subscription(user_id, context):
    for channel in CHANNELS:
        try:
            chat_member = await context.bot.get_chat_member(channel, user_id)
            if chat_member.status in ["left", "kicked"]:
                return False
        except Exception as e:
            logging.error(f"Obuna tekshirishda xatolik: {e}")
            return False
    return True


# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats["totalMessages"] += 1
    user_id = update.message.chat.id

    # Til tanlash tugmalari
    keyboard = [
        [InlineKeyboardButton("🇺🇿 O‘zbek", callback_data='lang_uz')],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data='lang_ru')],
        [InlineKeyboardButton("🇬🇧 English", callback_data='lang_en')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Tilni tanlang / Выберите язык / Choose a language:", reply_markup=reply_markup)


# Asosiy menyu
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, lang_code="uz"):
    keyboard = [
        [InlineKeyboardButton("🌍 Eco Challenge", callback_data='eco_challenge')],
        [InlineKeyboardButton("📢 Eco Alerts", callback_data='eco_alerts')],
        [InlineKeyboardButton("🎁 Eco Rewards", callback_data='eco_rewards')],
        [InlineKeyboardButton("📊 Eco Calculator", callback_data='eco_calculator')],
        [InlineKeyboardButton("🌳 Daraxt sotib olish", callback_data='tree_shop')],
        [InlineKeyboardButton("🌍 Havo sifati", callback_data='air_quality')],
        [InlineKeyboardButton("📊 Statistika", callback_data='bot_stats')],
        [InlineKeyboardButton("🌐 Tilni o‘zgartirish", callback_data='change_language')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(languages[lang_code]["start"], reply_markup=reply_markup)


# Tugmalarni boshqarish
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    # Tilni o'zgartirish
    if data.startswith("lang_"):
        lang_code = data.split("_")[1]
        userLanguage[user_id] = lang_code
        await query.edit_message_text(languages[lang_code]["language_selected"])
        await show_main_menu(query, context, lang_code)
        return

    # Boshqa funksiyalar
    lang_code = userLanguage.get(user_id, "uz")
    if data == "eco_challenge":
        await query.edit_message_text(languages[lang_code]["eco_challenge"])
    elif data == "eco_alerts":
        await query.edit_message_text(languages[lang_code]["eco_alerts"])
    elif data == "eco_rewards":
        await query.edit_message_text(languages[lang_code]["eco_rewards"])
    elif data == "eco_calculator":
        await query.edit_message_text(languages[lang_code]["eco_calculator"])
    elif data == "tree_shop":
        await show_tree_shop(query, lang_code)
    elif data == "air_quality":
        await query.edit_message_text(languages[lang_code]["aqi_request"])
    elif data == "bot_stats":
        await query.edit_message_text(languages[lang_code]["stats"](stats))
    elif data == "change_language":
        keyboard = [
            [InlineKeyboardButton("🇺🇿 O‘zbek", callback_data='lang_uz')],
            [InlineKeyboardButton("🇷🇺 Русский", callback_data='lang_ru')],
            [InlineKeyboardButton("🇬🇧 English", callback_data='lang_en')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("🌐 Tilni tanlang:", reply_markup=reply_markup)


# Daraxtlar ro'yxatini chiqarish
async def show_tree_shop(query, lang_code):
    keyboard = [
        [InlineKeyboardButton("🌲 Daraxt 1 - $10", callback_data='buy_tree_1')],
        [InlineKeyboardButton("🌳 Daraxt 2 - $15", callback_data='buy_tree_2')],
        [InlineKeyboardButton("🌴 Daraxt 3 - $20", callback_data='buy_tree_3')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(languages[lang_code]["tree_shop"], reply_markup=reply_markup)


# Daraxt sotib olish
async def buy_tree(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    tree_prices = {"1": 10, "2": 15, "3": 20}
    tree_id = query.data.split("_")[2]
    price = tree_prices.get(tree_id, "N/A")
    lang_code = userLanguage.get(query.from_user.id, "uz")
    await query.edit_message_text(f"✅ {languages[lang_code]['tree_shop']} {tree_id} sotib oldingiz! Narx: ${price}")


# Botni ishga tushirish
def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(CallbackQueryHandler(buy_tree, pattern='^buy_tree_\\d$'))
    application.run_polling()


if __name__ == "__main__":
    main()
