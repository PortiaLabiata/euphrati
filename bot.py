import process
import logging
from telegram import Update
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import InlineQueryHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

h_perc = 7.5
w_perc = 50
h_use = True
loc = 'rb'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Приветствую, боевой брат! Чтобы узнать, чем я могу вам помочь, введите /help.'
    )
    h_perc = 7.5
    w_perc = 50
    h_use = True
    loc = 'rb'

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Я - Эуфрация Киилер, штатный летописец, приписанный к легиону Сынов Хоруса. Вот список команд:\n'+\
            '/start - Начать всё сначала\n'+\
            '/help - Запросить поддержку\n'+\
            '/set_h_perc h - Задать высоту h (в процентах от высоты изображения) водяного знака.\n'+\
            '/set_w_perc w - Задать ширину w (в процентах от ширины изображения) водяного знака.\n'+\
            '/set_hw [h, w] - Использовать для подгонки размеров знака высоту (h) или ширину (w).\n'+\
            'Чтобы добавить водяной знак на изображение, просто пришлите его в чат. Присылайте несжатое изображение!'
    )

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Боюсь я не совсем вас понимаю, боевой брат! Возможно команда /help поможет вам разобраться, а если чувствуете, что разговор зашёл в тупик, попробуйте команду /start.'
    )

async def compressed_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await context.bot.get_file(update.message.photo[-1])
    file.download_to_drive('images/temp.png')
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'{update.message.photo}'
    )
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('images/temp.png', 'rb'))

async def set_h_perc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global h_perc
    h_perc = float(context.args[0])
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'Высота водяного знака задана в {h_perc}%'
    )

async def set_w_perc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global w_perc
    w_perc = float(context.args[0])
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'Ширина водяного знака задана в {w_perc}%'
    )

async def set_hw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global h_use
    if context.args[0] == 'h':
        h_use = True
    elif context.args[0] == 'w':
        h_use = False
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Прошу прощения, боевой брат, но ваши аргументы мне не понятны! (Передан неверный аргумент).'
        )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Для подгонки будет использоваться {'высота' if h_use else 'ширина'}."
    )

async def process_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await context.bot.get_file(update.message.document)
    filename = update.message.document.file_name
    await file.download_to_drive(f'images/{filename}')
    img, wmk = process.load(f'images/{filename}', 'watermark.png')
    process.resize(img, wmk, height_perc=h_perc, width_perc=w_perc, h_use=h_use)
    process.paste_watermark(img, wmk)
    img.save(f'images/{filename}')
    await context.bot.send_document(chat_id=update.effective_chat.id, document=open(f'images/{filename}', 'rb'))

token = next(open('token.txt')).strip()
app = ApplicationBuilder().token(token).build()

start_handler = CommandHandler('start', start)
help_handler = CommandHandler('help', help)
image_handler = MessageHandler(filters.Document.ALL, process_image)
comp_handler = MessageHandler(filters.PHOTO, compressed_image)
set_h_handler = CommandHandler('set_h_perc', set_h_perc)
set_w_handler = CommandHandler('set_w_perc', set_w_perc)
set_hw_handler = CommandHandler('set_hw', set_hw)
unknown_handler = MessageHandler(filters.TEXT | filters.COMMAND, unknown_command)

handlers = [start_handler, help_handler, image_handler, set_h_handler,
            set_w_handler, comp_handler, set_hw_handler, unknown_handler]

app.add_handlers(handlers)

app.run_polling()
