import os
import logging
import random
import asyncio
import sys
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

# --- UPTIME ROBOT UCHUN KICHIK VEB SERVER ---
app_flask = Flask('')

@app_flask.route('/')
def home():
    return "Bot tirik va ishlamoqda! 🚀"

def keep_alive():
    port = int(os.environ.get("PORT", 10000))
    def run():
        app_flask.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    t = Thread(target=run)
    t.daemon = True
    t.start()
    print("🌍 Flask veb server fonda ishga tushdi...")
# --------------------------------------------

BOT_TOKEN = os.getenv("BOT_TOKEN", "8948394212:AAF0QBMz4xg1pQCbgM4OU4K0MA3q3Aa6asI")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

WORDS = {
    "Interfaol olam": [
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

GRAMMAR_TESTS = [
    {"question": "To'g'ri javobni tanlang:\nShe ___ a student.", "options": ["is", "are", "am", "be"], "answer": "is", "explanation": "She - 3-shaxs birlik uchun 'is' ishlatiladi."},
    {"question": "To'g'ri javobni tanlang:\nThey ___ happy.", "options": ["is", "are", "am", "was"], "answer": "are", "explanation": "They - ko'plik uchun 'are' ishlatiladi."},
    {"question": "To'g'ri javobni tanlang:\nI ___ from Uzbekistan.", "options": ["is", "are", "am", "be"], "answer": "am", "explanation": "I - birinchi shaxs uchun 'am' ishlatiladi."},
    {"question": "To'g'ri javobni tanlang:\nHe ___ football yesterday.", "options": ["play", "plays", "played", "playing"], "answer": "played", "explanation": "Yesterday = o'tgan zamon, shuning uchun 'played' (Past Simple)."},
    {"question": "To'g'ri javobni tanlang:\nShe ___ to school every day.", "options": ["go", "goes", "going", "went"], "answer": "goes", "explanation": "She - 3-shaxs birlik + har doim = Present Simple: 'goes'."},
    {"question": "To'g'ri javobni tanlang:\n___ you speak English?", "options": ["Do", "Does", "Are", "Is"], "answer": "Do", "explanation": "You bilan savol = 'Do you...'."},
    {"question": "To'g'ri javobni tanlang:\nThere ___ many books on the table.", "options": ["is", "are", "am", "be"], "answer": "are", "explanation": "'Many books' ko'plik, shuning uchun 'are'."},
    {"question": "To'g'ri javobni tanlang:\nI ___ never been to London.", "options": ["have", "has", "had", "am"], "answer": "have", "explanation": "Present Perfect: I have + 3-forma (been)."},
    {"question": "To'g'ri javobni tanlang:\nThe cat is ___ than the dog.", "options": ["small", "smaller", "smallest", "more small"], "answer": "smaller", "explanation": "Ikki narsani solishtirish = Comparative: smaller."},
    {"question": "To'g'ri javobni tanlang:\nThis is ___ book I have ever read.", "options": ["good", "better", "best", "the best"], "answer": "the best", "explanation": "Superlative daraja: the best (eng yaxshi)."},
]

user_data = {}

def get_user(user_id):
    if user_id not in user_data:
        user_data[user_id] = {
            "score": 0, "total_questions": 0, "correct_answers": 0,
            "learned_words": [], "current_quiz": None, "current_category": None,
        }
    return user_data[user_id]

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
    text = f"Salom, {user.first_name}! 👋\n\n🇬🇧 *Ingliz tili o'rganish botiga xush kelibsiz!*\n\nQaysi biri bilan boshlaysiz? 👇"
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def learn_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton(f"📂 {cat}", callback_data=f"cat_{cat}")] for cat in WORDS.keys()]
    keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="main_menu")])
    await query.edit_message_text("📚 *So'z o'rganish*\n\nQaysi kategoriyani o'rganmoqchisiz?", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def show_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category = query.data.replace("cat_", "")
    words = WORDS.get(category, [])
    user = get_user(query.from_user.id)
    user["current_category"] = category
    text = f"📂 *{category}* kategoriyasi\n\n"
    for i, word in enumerate(words, 1):
        text += f"{i}. 🇺🇿 *{word['uz']}* → 🇬🇧 *{word['en']}*\n💬 _{word['example']}_\n\n"
    keyboard = [[InlineKeyboardButton("🧪 Shu kategoriyani test qilish", callback_data=f"quiz_cat_{category}")], [InlineKeyboardButton("🔙 Orqaga", callback_data="learn_words")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def quiz_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category = query.data.replace("quiz_cat_", "")
    words = WORDS.get(category, [])
    if len(words) < 4:
        await query.edit_message_text("Bu kategoriyada yetarli so'z yo'q!")
        return
    correct = random.choice(words)
    wrong_choices = random.sample([w for w in words if w["en"] != correct["en"]], min(3, len(words)-1))
    all_choices = [correct] + wrong_choices
    random.shuffle(all_choices)
    user = get_user(query.from_user.id)
    user["current_quiz"] = {"correct": correct["en"], "category": category, "type": "word"}
    keyboard = [[InlineKeyboardButton(choice["en"], callback_data=f"word_ans_{choice['en']}")] for choice in all_choices]
    keyboard.append([InlineKeyboardButton("🔙 Kategoriyaga qaytish", callback_data=f"cat_{category}")])
    await query.edit_message_text(f"🧪 *So'z testi*\n\n🇺🇿 *{correct['uz']}* so'zining inglizcha tarjimasi qaysi?", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def word_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    all_words = []
    for words in WORDS.values():
        all_words.extend(words)
    correct = random.choice(all_words)
    wrong_choices = random.sample([w for w in all_words if w["en"] != correct["en"]], 3)
    all_choices = [correct] + wrong_choices
    random.shuffle(all_choices)
    user = get_user(query.from_user.id)
    user["current_quiz"] = {"correct": correct["en"], "type": "word"}
    keyboard = [[InlineKeyboardButton(choice["en"], callback_data=f"word_ans_{choice['en']}")] for choice in all_choices]
    keyboard.append([InlineKeyboardButton("🔙 Bosh menyu", callback_data="main_menu")])
    await query.edit_message_text(f"🧪 *So'z testi*\n\n🇺🇿 *{correct['uz']}* so'zining inglizcha tarjimasi qaysi?", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

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
        result_text, emoji = "✅ *To'g'ri!* Barakalla! 🎉", "🎊"
    else:
        result_text, emoji = f"❌ *Noto'g'ri!*\n\nTo'g'ri javob: *{correct}*", "😔"
    correct_word = next((w for words in WORDS.values() for w in words if w["en"] == correct), None)
    example_text = f"\n\n💬 Misol: _{correct_word['example']}_" if correct_word else ""
    accuracy = round(user["correct_answers"] / user["total_questions"] * 100) if user["total_questions"] > 0 else 0
    keyboard = [[InlineKeyboardButton("➡️ Keyingi savol", callback_data="word_test")], [InlineKeyboardButton("📊 Natijalarim", callback_data="my_stats")], [InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]]
    await query.edit_message_text(f"{emoji} {result_text}{example_text}\n\n📊 Sizning natijangiz: {user['correct_answers']}/{user['total_questions']} ({accuracy}%)", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def grammar_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    test = random.choice(GRAMMAR_TESTS)
    user = get_user(query.from_user.id)
    user["current_quiz"] = {"correct": test["answer"], "explanation": test["explanation"], "type": "grammar"}
    options = test["options"].copy()
    random.shuffle(options)
    keyboard = [[InlineKeyboardButton(opt, callback_data=f"gram_ans_{opt}")] for opt in options]
    keyboard.append([InlineKeyboardButton("🔙 Bosh menyu", callback_data="main_menu")])
    await query.edit_message_text(f"📝 *Grammar testi*\n\n{test['question']}", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def check_grammar_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chosen = query.data.replace("gram_ans_", "")
    user = get_user(query.from_user.id)
    quiz = user.get("current_quiz")
    if not quiz:
        await start(update, context)
        return
    correct, explanation = quiz["correct"], quiz.get("explanation", "")
    user["total_questions"] = user.get("total_questions", 0) + 1
    if chosen == correct:
        user["correct_answers"] = user.get("correct_answers", 0) + 1
        result_text, emoji = "✅"