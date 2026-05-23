import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

# Bot token - BotFather dan olingan token
BOT_TOKEN = "8948394212:AAF0QBMz4xg1pQCbgM4OU4K0MA3q3Aa6asI"  # <-- Shu yerga o'z tokeningizni qo'ying

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# So'zlar ro'yxati (kategoriyalar bo'yicha)
WORDS = {
    "Kundalik hayot": [
        {"uz": "non", "en": "bread", "example": "I eat bread every morning."},
        {"uz": "suv", "en": "water", "example": "Please give me some water."},
        {"uz": "uy", "en": "house", "example": "This is my house."},
        {"uz": "kitob", "en": "book", "example": "I love reading books."},
        {"uz": "do'st", "en": "friend", "example": "She is my best friend."},
        {"uz": "maktab", "en": "school", "example": "I go to school every day."},
        {"uz": "o'qituvchi", "en": "teacher", "example": "My teacher is very kind."},
        {"uz": "telefon", "en": "phone", "example": "My phone is new."},
        {"uz": "mashina", "en": "car", "example": "He drives a red car."},
        {"uz": "ovqat", "en": "food", "example": "The food is delicious."},
    ],
    "Hayvonlar": [
        {"uz": "it", "en": "dog", "example": "The dog is barking."},
        {"uz": "mushuk", "en": "cat", "example": "I have a cute cat."},
        {"uz": "qush", "en": "bird", "example": "The bird is flying."},
        {"uz": "ot", "en": "horse", "example": "The horse runs fast."},
        {"uz": "fil", "en": "elephant", "example": "Elephants are very big."},
        {"uz": "sher", "en": "lion", "example": "The lion is the king."},
        {"uz": "baliq", "en": "fish", "example": "Fish live in water."},
        {"uz": "qo'y", "en": "sheep", "example": "Sheep eat grass."},
    ],
    "Ranglar": [
        {"uz": "qizil", "en": "red", "example": "The apple is red."},
        {"uz": "ko'k", "en": "blue", "example": "The sky is blue."},
        {"uz": "yashil", "en": "green", "example": "Grass is green."},
        {"uz": "sariq", "en": "yellow", "example": "The sun is yellow."},
        {"uz": "oq", "en": "white", "example": "Snow is white."},
        {"uz": "qora", "en": "black", "example": "The night is black."},
        {"uz": "to'q sariq", "en": "orange", "example": "Oranges are orange."},
        {"uz": "binafsha", "en": "purple", "example": "She likes purple flowers."},
    ],
    "Sonlar": [
        {"uz": "bir", "en": "one", "example": "I have one apple."},
        {"uz": "ikki", "en": "two", "example": "She has two cats."},
        {"uz": "uch", "en": "three", "example": "There are three books."},
        {"uz": "to'rt", "en": "four", "example": "The table has four legs."},
        {"uz": "besh", "en": "five", "example": "I need five minutes."},
        {"uz": "o'n", "en": "ten", "example": "I have ten fingers."},
        {"uz": "yuz", "en": "hundred", "example": "One hundred students."},
        {"uz": "ming", "en": "thousand", "example": "A thousand stars."},
    ],
}

# Grammar testlar
GRAMMAR_TESTS = [
    {
        "question": "To'g'ri javobni tanlang:\nShe ___ a student.",
        "options": ["is", "are", "am", "be"],
        "answer": "is",
        "explanation": "She - 3-shaxs birlik uchun 'is' ishlatiladi."
    },
    {
        "question": "To'g'ri javobni tanlang:\nThey ___ happy.",
        "options": ["is", "are", "am", "was"],
        "answer": "are",
        "explanation": "They - ko'plik uchun 'are' ishlatiladi."
    },
    {
        "question": "To'g'ri javobni tanlang:\nI ___ from Uzbekistan.",
        "options": ["is", "are", "am", "be"],
        "answer": "am",
        "explanation": "I - birinchi shaxs uchun 'am' ishlatiladi."
    },
    {
        "question": "To'g'ri javobni tanlang:\nHe ___ football yesterday.",
        "options": ["play", "plays", "played", "playing"],
        "answer": "played",
        "explanation": "Yesterday = o'tgan zamon, shuning uchun 'played' (Past Simple)."
    },
    {
        "question": "To'g'ri javobni tanlang:\nShe ___ to school every day.",
        "options": ["go", "goes", "going", "went"],
        "answer": "goes",
        "explanation": "She - 3-shaxs birlik + har doim = Present Simple: 'goes'."
    },
    {
        "question": "To'g'ri javobni tanlang:\n___ you speak English?",
        "options": ["Do", "Does", "Are", "Is"],
        "answer": "Do",
        "explanation": "You bilan savol = 'Do you...'."
    },
    {
        "question": "To'g'ri javobni tanlang:\nThere ___ many books on the table.",
        "options": ["is", "are", "am", "be"],
        "answer": "are",
        "explanation": "'Many books' ko'plik, shuning uchun 'are'."
    },
    {
        "question": "To'g'ri javobni tanlang:\nI ___ never been to London.",
        "options": ["have", "has", "had", "am"],
        "answer": "have",
        "explanation": "Present Perfect: I have + 3-forma (been)."
    },
    {
        "question": "To'g'ri javobni tanlang:\nThe cat is ___ than the dog.",
        "options": ["small", "smaller", "smallest", "more small"],
        "answer": "smaller",
        "explanation": "Ikki narsani solishtirish = Comparative: smaller."
    },
    {
        "question": "To'g'ri javobni tanlang:\nThis is ___ book I have ever read.",
        "options": ["good", "better", "best", "the best"],
        "answer": "the best",
        "explanation": "Superlative daraja: the best (eng yaxshi)."
    },
]

# Foydalanuvchi ma'lumotlari
user_data = {}

def get_user(user_id):
    if user_id not in user_data:
        user_data[user_id] = {
            "score": 0,
            "total_questions": 0,
            "correct_answers": 0,
            "learned_words": [],
            "current_quiz": None,
            "current_category": None,
        }
    return user_data[user_id]

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_user(user.id)
    
    keyboard = [
        [InlineKeyboardButton("📚 So'z o'rganish", callback_data="learn_words")],
        [InlineKeyboardButton("🧪 So'z testi", callback_data="word_test")],
        [InlineKeyboardButton("📝 Grammar testi", callback_data="grammar_test")],
        [InlineKeyboardButton("📊 Mening natijalarim", callback_data="my_stats")],
        [InlineKeyboardButton("ℹ️ Yordam", callback_data="help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        f"Salom, {user.first_name}! 👋\n\n"
        "🇬🇧 *Ingliz tili o'rganish botiga xush kelibsiz!*\n\n"
        "Bu bot orqali siz:\n"
        "✅ Yangi so'zlar o'rganasiz\n"
        "✅ So'zlarni test qilasiz\n"
        "✅ Grammar mashq qilasiz\n"
        "✅ O'z natijalaringizni ko'rasiz\n\n"
        "Qaysi biri bilan boshlaysiz? 👇"
    )
    
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

# So'z o'rganish - kategoriya tanlash
async def learn_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = []
    for category in WORDS.keys():
        keyboard.append([InlineKeyboardButton(f"📂 {category}", callback_data=f"cat_{category}")])
    keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="main_menu")])
    
    await query.edit_message_text(
        "📚 *So'z o'rganish*\n\nQaysi kategoriyani o'rganmoqchisiz?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# Kategoriya so'zlari
async def show_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    category = query.data.replace("cat_", "")
    words = WORDS.get(category, [])
    user = get_user(query.from_user.id)
    user["current_category"] = category
    
    text = f"📂 *{category}* kategoriyasi\n\n"
    for i, word in enumerate(words, 1):
        text += f"{i}. 🇺🇿 *{word['uz']}* → 🇬🇧 *{word['en']}*\n"
        text += f"   💬 _{word['example']}_\n\n"
    
    keyboard = [
        [InlineKeyboardButton("🧪 Shu kategoriyani test qilish", callback_data=f"quiz_cat_{category}")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="learn_words")],
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# So'z testi (kategoriyadan)
async def quiz_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    category = query.data.replace("quiz_cat_", "")
    words = WORDS.get(category, [])
    
    if len(words) < 4:
        await query.edit_message_text("Bu kategoriyada yetarli so'z yo'q!")
        return
    
    # Random so'z tanlash
    correct = random.choice(words)
    wrong_words = [w for w in words if w["en"] != correct["en"]]
    wrong_choices = random.sample(wrong_words, min(3, len(wrong_words)))
    
    all_choices = [correct] + wrong_choices
    random.shuffle(all_choices)
    
    user = get_user(query.from_user.id)
    user["current_quiz"] = {
        "correct": correct["en"],
        "category": category,
        "type": "word"
    }
    
    keyboard = []
    for choice in all_choices:
        keyboard.append([InlineKeyboardButton(choice["en"], callback_data=f"word_ans_{choice['en']}")])
    keyboard.append([InlineKeyboardButton("🔙 Kategoriyaga qaytish", callback_data=f"cat_{category}")])
    
    await query.edit_message_text(
        f"🧪 *So'z testi*\n\n"
        f"🇺🇿 *{correct['uz']}* so'zining inglizcha tarjimasi qaysi?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# So'z testi (umumiy)
async def word_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    all_words = []
    for words in WORDS.values():
        all_words.extend(words)
    
    correct = random.choice(all_words)
    wrong_words = [w for w in all_words if w["en"] != correct["en"]]
    wrong_choices = random.sample(wrong_words, 3)
    
    all_choices = [correct] + wrong_choices
    random.shuffle(all_choices)
    
    user = get_user(query.from_user.id)
    user["current_quiz"] = {
        "correct": correct["en"],
        "type": "word"
    }
    user["total_questions"] = user.get("total_questions", 0) + 1
    
    keyboard = []
    for choice in all_choices:
        keyboard.append([InlineKeyboardButton(choice["en"], callback_data=f"word_ans_{choice['en']}")])
    keyboard.append([InlineKeyboardButton("🔙 Bosh menyu", callback_data="main_menu")])
    
    await query.edit_message_text(
        f"🧪 *So'z testi*\n\n"
        f"🇺🇿 *{correct['uz']}* so'zining inglizcha tarjimasi qaysi?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# So'z javobini tekshirish
async def check_word_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    chosen = query.data.replace("word_ans_", "")
    user = get_user(query.from_user.id)
    quiz = user.get("current_quiz")
    
    if not quiz:
        await start(update, context)
        return
    
    correct = quiz["correct"]
    user["total_questions"] = user.get("total_questions", 0) + 1
    
    if chosen == correct:
        user["correct_answers"] = user.get("correct_answers", 0) + 1
        result_text = "✅ *To'g'ri!* Barakalla! 🎉"
        emoji = "🎊"
    else:
        result_text = f"❌ *Noto'g'ri!*\n\nTo'g'ri javob: *{correct}*"
        emoji = "😔"
    
    correct_word = None
    for words in WORDS.values():
        for w in words:
            if w["en"] == correct:
                correct_word = w
                break
    
    example_text = ""
    if correct_word:
        example_text = f"\n\n💬 Misol: _{correct_word['example']}_"
    
    accuracy = 0
    if user["total_questions"] > 0:
        accuracy = round(user["correct_answers"] / user["total_questions"] * 100)
    
    keyboard = [
        [InlineKeyboardButton("➡️ Keyingi savol", callback_data="word_test")],
        [InlineKeyboardButton("📊 Natijalarim", callback_data="my_stats")],
        [InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")],
    ]
    
    await query.edit_message_text(
        f"{emoji} {result_text}{example_text}\n\n"
        f"📊 Sizning natijangiz: {user['correct_answers']}/{user['total_questions']} ({accuracy}%)",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# Grammar testi
async def grammar_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    test = random.choice(GRAMMAR_TESTS)
    user = get_user(query.from_user.id)
    user["current_quiz"] = {
        "correct": test["answer"],
        "explanation": test["explanation"],
        "type": "grammar"
    }
    
    options = test["options"].copy()
    random.shuffle(options)
    
    keyboard = []
    for option in options:
        keyboard.append([InlineKeyboardButton(option, callback_data=f"gram_ans_{option}")])
    keyboard.append([InlineKeyboardButton("🔙 Bosh menyu", callback_data="main_menu")])
    
    await query.edit_message_text(
        f"📝 *Grammar testi*\n\n{test['question']}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# Grammar javobini tekshirish
async def check_grammar_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    chosen = query.data.replace("gram_ans_", "")
    user = get_user(query.from_user.id)
    quiz = user.get("current_quiz")
    
    if not quiz:
        await start(update, context)
        return
    
    correct = quiz["correct"]
    explanation = quiz.get("explanation", "")
    user["total_questions"] = user.get("total_questions", 0) + 1
    
    if chosen == correct:
        user["correct_answers"] = user.get("correct_answers", 0) + 1
        result_text = "✅ *To'g'ri!* Zo'r! 🎉"
        emoji = "🎊"
    else:
        result_text = f"❌ *Noto'g'ri!*\nTo'g'ri javob: *{correct}*"
        emoji = "😔"
    
    accuracy = 0
    if user["total_questions"] > 0:
        accuracy = round(user["correct_answers"] / user["total_questions"] * 100)
    
    keyboard = [
        [InlineKeyboardButton("➡️ Keyingi grammar savol", callback_data="grammar_test")],
        [InlineKeyboardButton("📊 Natijalarim", callback_data="my_stats")],
        [InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")],
    ]
    
    await query.edit_message_text(
        f"{emoji} {result_text}\n\n"
        f"💡 *Izoh:* {explanation}\n\n"
        f"📊 Sizning natijangiz: {user['correct_answers']}/{user['total_questions']} ({accuracy}%)",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# Natijalar
async def my_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = get_user(query.from_user.id)
    total = user.get("total_questions", 0)
    correct = user.get("correct_answers", 0)
    accuracy = round(correct / total * 100) if total > 0 else 0
    
    if accuracy >= 80:
        medal = "🥇"
        comment = "Ajoyib! Siz juda yaxshi o'qiyapsiz!"
    elif accuracy >= 60:
        medal = "🥈"
        comment = "Yaxshi! Davom eting!"
    elif accuracy >= 40:
        medal = "🥉"
        comment = "O'rta daraja. Ko'proq mashq qiling!"
    elif total == 0:
        medal = "📚"
        comment = "Hali test ishlamadingiz. Boshlang!"
    else:
        medal = "💪"
        comment = "Qiyin ekan, lekin davom eting!"
    
    keyboard = [
        [InlineKeyboardButton("🔄 Natijalarni qayta boshlash", callback_data="reset_stats")],
        [InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")],
    ]
    
    await query.edit_message_text(
        f"📊 *Sizning natijalaringiz*\n\n"
        f"{medal} Daraja: {'Boshlang\'ich' if total < 10 else 'O\'rta' if total < 30 else 'Yuqori'}\n\n"
        f"✅ To'g'ri javoblar: *{correct}*\n"
        f"❌ Xato javoblar: *{total - correct}*\n"
        f"📝 Jami savollar: *{total}*\n"
        f"🎯 Aniqlik: *{accuracy}%*\n\n"
        f"💬 {comment}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# Natijalarni reset
async def reset_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_data[user_id] = {
        "score": 0,
        "total_questions": 0,
        "correct_answers": 0,
        "learned_words": [],
        "current_quiz": None,
    }
    
    keyboard = [[InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]]
    
    await query.edit_message_text(
        "✅ Natijalaringiz tozalandi! Yangi boshlang! 💪",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Yordam
async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [[InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]]
    
    await query.edit_message_text(
        "ℹ️ *Yordam*\n\n"
        "🤖 Bu bot ingliz tilini o'rganishga yordam beradi!\n\n"
        "📚 *So'z o'rganish* - Kategoriyalar bo'yicha so'zlarni ko'ring\n\n"
        "🧪 *So'z testi* - O'zbek so'zini inglizchaga tarjima qiling\n\n"
        "📝 *Grammar testi* - Grammatika qoidalarini mashq qiling\n\n"
        "📊 *Natijalarim* - O'z natijalaringizni ko'ring\n\n"
        "💡 *Maslahat:* Har kuni 10-15 daqiqa mashq qiling!",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# Bosh menyu
async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

# Noma'lum xabar
async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]]
    await update.message.reply_text(
        "Bot bilan faqat tugmalar orqali muloqot qiling! 👇\n/start ni bosing",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Komandalar
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", main_menu))
    
    # Tugmalar
    app.add_handler(CallbackQueryHandler(learn_words, pattern="^learn_words$"))
    app.add_handler(CallbackQueryHandler(show_category, pattern="^cat_"))
    app.add_handler(CallbackQueryHandler(quiz_category, pattern="^quiz_cat_"))
    app.add_handler(CallbackQueryHandler(word_test, pattern="^word_test$"))
    app.add_handler(CallbackQueryHandler(check_word_answer, pattern="^word_ans_"))
    app.add_handler(CallbackQueryHandler(grammar_test, pattern="^grammar_test$"))
    app.add_handler(CallbackQueryHandler(check_grammar_answer, pattern="^gram_ans_"))
    app.add_handler(CallbackQueryHandler(my_stats, pattern="^my_stats$"))
    app.add_handler(CallbackQueryHandler(reset_stats, pattern="^reset_stats$"))
    app.add_handler(CallbackQueryHandler(help_menu, pattern="^help$"))
    app.add_handler(CallbackQueryHandler(main_menu, pattern="^main_menu$"))
    
    # Noma'lum xabarlar
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_message))
    
    print("✅ Bot ishga tushdi!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()