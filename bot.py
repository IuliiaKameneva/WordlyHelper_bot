import logging

from telegram import ParseMode
from telegram import Update, ForceReply, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

import wordly_scripts
import numpy as np

logger = logging.getLogger(__name__)

# Text file with bot's id 
BOT_ID_FILE = 'wordly_helper_bot_id.txt'

# Store bot screaming status
screaming = False

# Pre-assign menu text
FIRST_MENU = "<b>Menu 1</b>\n\nA beautiful menu with a shiny inline button."
SECOND_MENU = "<b>Menu 2</b>\n\nA better menu with even more shiny inline buttons."

# Pre-assign button text
NEXT_BUTTON = "Next"
BACK_BUTTON = "Back"
TUTORIAL_BUTTON = "Tutorial"

# Build keyboards
FIRST_MENU_MARKUP = InlineKeyboardMarkup([[
    InlineKeyboardButton(NEXT_BUTTON, callback_data=NEXT_BUTTON)
]])
SECOND_MENU_MARKUP = InlineKeyboardMarkup([
    [InlineKeyboardButton(BACK_BUTTON, callback_data=BACK_BUTTON)],
    [InlineKeyboardButton(TUTORIAL_BUTTON, url="https://core.telegram.org/bots/api")]
])

POSSIBLE_WORDS = {}#load_words()  # Загрузка всех слов
BEST_WORD = {}# = np.array(['н', 'о', 'р', 'к', 'а'])

def echo(update: Update, context: CallbackContext) -> None:
    """
    This function would be added to the dispatcher as a handler for messages coming from the Bot API
    """

    # Print to console
    print(f'{update.message.from_user.first_name} wrote {update.message.text}')

    feedback = update.message.text.upper() # TODO: check the correctness TODO: two formats feedback and word+feedback
    if wordly_scripts.checkFeedback(feedback):
        best_word_index = np.prod(POSSIBLE_WORDS[update.message.chat_id]==BEST_WORD[update.message.chat_id], axis=1).argmax()
        POSSIBLE_WORDS[update.message.chat_id] = np.delete(POSSIBLE_WORDS[update.message.chat_id], best_word_index, axis=0)
        POSSIBLE_WORDS[update.message.chat_id] = wordly_scripts.filter_words(POSSIBLE_WORDS[update.message.chat_id], \
                                                                             BEST_WORD[update.message.chat_id], feedback)
        if len(POSSIBLE_WORDS[update.message.chat_id]) == 1:
            print(f"The answer is: {POSSIBLE_WORDS[update.message.chat_id][0]}")
        BEST_WORD[update.message.chat_id] = max(POSSIBLE_WORDS[update.message.chat_id], \
                                                key=lambda w: wordly_scripts.calculate_entropy(w, POSSIBLE_WORDS[update.message.chat_id]))

        context.bot.send_message(
            update.message.chat_id,
            'Теперь попробуй слово '+''.join(BEST_WORD[update.message.chat_id]).upper(),
            # To preserve the markdown, we attach entities (bold, italic...)
            entities=update.message.entities
        )
    else:
        context.bot.send_message(
            update.message.chat_id,
            'Неверное сообщение! Формат: XXXXX, где X может быть одной из трёх букв(B-Black, Y-Yellow, G-Green)',
            # To preserve the markdown, we attach entities (bold, italic...)
            entities=update.message.entities
        )

#     if screaming and update.message.text:
#         context.bot.send_message(
#             update.message.chat_id,
#             update.message.text.upper(),
#             # To preserve the markdown, we attach entities (bold, italic...)
#             entities=update.message.entities
#         )
#     else:
#         # This is equivalent to forwarding, without the sender's name
#         update.message.copy(update.message.chat_id)

        
def start(update: Update, context: CallbackContext) -> None:
    """
    This function would be added to the dispatcher as a handler for messages coming from the Bot API
    """
    POSSIBLE_WORDS[update.message.chat_id] = wordly_scripts.load_words()  # Загрузка всех слов
    BEST_WORD[update.message.chat_id] = np.array(['н', 'о', 'р', 'к', 'а'])
    
    context.bot.send_message(
            update.message.chat_id,
            'Добро подаловать в WordlyHelper!\nДля начала я предлагаю тебе слово '+''.join(BEST_WORD[update.message.chat_id]).upper(),
            # To preserve the markdown, we attach entities (bold, italic...)
            entities=update.message.entities
        )
        


def scream(update: Update, context: CallbackContext) -> None:
    """
    This function handles the /scream command
    """

    global screaming
    screaming = True


def whisper(update: Update, context: CallbackContext) -> None:
    """
    This function handles /whisper command
    """

    global screaming
    screaming = False


def menu(update: Update, context: CallbackContext) -> None:
    """
    This handler sends a menu with the inline buttons we pre-assigned above
    """

    context.bot.send_message(
        update.message.from_user.id,
        FIRST_MENU,
        parse_mode=ParseMode.HTML,
        reply_markup=FIRST_MENU_MARKUP
    )


def button_tap(update: Update, context: CallbackContext) -> None:
    """
    This handler processes the inline buttons on the menu
    """

    data = update.callback_query.data
    text = ''
    markup = None

    if data == NEXT_BUTTON:
        text = SECOND_MENU
        markup = SECOND_MENU_MARKUP
    elif data == BACK_BUTTON:
        text = FIRST_MENU
        markup = FIRST_MENU_MARKUP

    # Close the query to end the client-side loading animation
    update.callback_query.answer()

    # Update message content with corresponding menu section
    update.callback_query.message.edit_text(
        text,
        ParseMode.HTML,
        reply_markup=markup
    )


def main() -> None:
    updater = Updater(open(BOT_ID_FILE, 'r').readline())

    # Get the dispatcher to register handlers
    # Then, we register each handler and the conditions the update must meet to trigger it
    print ('Get the dispatcher to register handlers')
    dispatcher = updater.dispatcher

    # Register commands
    print ('Register commands')
    dispatcher.add_handler(CommandHandler("scream", scream))
    dispatcher.add_handler(CommandHandler("whisper", whisper))
    dispatcher.add_handler(CommandHandler("menu", menu))
    dispatcher.add_handler(CommandHandler("start", start))

    # Register handler for inline buttons
    print ('Register handler for inline buttons')
    dispatcher.add_handler(CallbackQueryHandler(button_tap))

    # Echo any message that is not a command
    print ('Echo any message that is not a command')
    dispatcher.add_handler(MessageHandler(~Filters.command, echo))

    # Start the Bot
    print ('Start the Bot')
    updater.start_polling()

    # Run the bot until you press Ctrl-C
    print ('Run.')
    updater.idle()


if __name__ == '__main__':
    main()