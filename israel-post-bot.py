#!/usr/bin/env python3
"""Israel Post Telegram Bot - Track your packages via Telegram

Make sure you have your bot token saved in a file named 'token'.
Github: https://github.com/LiranV/israel-post-bot
"""

import json
import logging
import urllib.request
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, RegexHandler, Filters
from bs4 import BeautifulSoup
import usersDAO
import packagesDAO

TRACKING_URL = "http://www.israelpost.co.il/itemtrace.nsf/trackandtraceJSON?OpenAgent&lang=en&itemcode={}"
TOKEN_FILE = "token"
CHOOSING, TYPING_NEW_ID = range(2)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

users = usersDAO.UsersDAO()
packages = packagesDAO.PackagesDAO()


def start_cmd(bot, update):
    logger.info("Received 'start' from user '{}'".format(update.message.from_user["id"]))
    users.add_user(update.message.from_user["id"], update.message.chat_id)
    start_message = ("Israel Post Telegram Bot at your service!\n"
                    "For help type '/help'")
    bot.sendMessage(chat_id=update.message.chat_id, text=start_message)


def track_cmd(bot, update):
    user_id = update.message.from_user["id"]
    custom_keyboard = [["New Package"]]
    ids_list = packages.get_tracking_id_list(user_id)
    for tracking_id in ids_list:
        custom_keyboard.append([tracking_id])
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=True)
    bot.sendMessage(chat_id=update.message.chat_id,
                    text="You can send '/cancel' to end the conversation at any time.\n"
                    "Please choose a package to track:",
                    reply_markup=reply_markup)
    return CHOOSING


def get_new_tracking_id(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id,
                    text="Please send me the package tracking ID.",
                    reply_markup=ReplyKeyboardRemove())
    return TYPING_NEW_ID


def tracking_reply(bot, update):
    user_id = update.message.from_user["id"]
    tracking_id = update.message.text
    try:
        tracking_text = get_tracking_information(tracking_id)
    except ValueError as e:
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="I'm sorry, but this tracking ID is invalid.\n"
                        "You should try using '/track' again.")
        return ConversationHandler.END

    packages.update_package(user_id, tracking_id, tracking_text)
    bot.sendMessage(chat_id=update.message.chat_id,
                    text=tracking_text)
    return ConversationHandler.END


def gen_help_menu():
    global commands
    global HELP_MENU
    header = ("Israel Post Telegram Bot\n\n"
              "Available commands:\n")
    message = [header]
    for command in commands:
        message.append("/{} - {}".format(command, commands[command].info))
    HELP_MENU = "\n".join(message)


def help_cmd(bot, update):
    help_text = ("*Israel Post Telegram Bot*\n\n"
                 "Available Commands:\n"
                 "/start - Display welcome message\n"
                 "/help - Display this message\n"
                 "/track - Track packages\n"
                 "\nCreated by Liran Vaknin\n"
                 "[Project page on GitHub](https://github.com/LiranV/israel-post-bot)")
    bot.sendMessage(chat_id=update.message.chat_id,
                    text=help_text,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True)


def cancel_conversation(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id,
                    text="Bye!",
                    reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def read_token():
    with open(TOKEN_FILE, 'r') as f:
        token = f.read().strip("\n")
        logger.info("Bot token: {}".format(token))
        return token


def get_tracking_information(tracking_id):
    with urllib.request.urlopen(TRACKING_URL.format(tracking_id)) as response:
        data = json.loads(response.read().decode("utf-8"))
    if data["data_type"].startswith("ERROR"):
        raise ValueError("Invalid tracking ID")
    tracking_data = data["itemcodeinfo"]
    if tracking_data.startswith("There is no information"):
        return tracking_data[:tracking_data.index("<br>")]
    soup = BeautifulSoup(tracking_data, "html.parser")
    table = soup.find("table")
    table_data = [[cell.get_text().strip() for cell in row.find_all("td")]
                  for row in table.find_all("tr")]
    return "\n".join(table_data[1])


def unknown_update(bot, update):
    message = "I'm sorry but I didn't understand that.\n"
    "Please refer to '/help' for the available commands."
    bot.sendMessage(chat_id=update.message.chat_id, text=message)


def error(bot, update, error):
    logger.warn("Update '{}' caused error '{}'".format(update, error))


def main():
    updater = Updater(token=read_token())
    dispatcher = updater.dispatcher

    tracking_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("track", track_cmd)],
        states={
            CHOOSING: [RegexHandler("^(New Package)$", get_new_tracking_id),
                       MessageHandler((Filters.text), tracking_reply)],
            TYPING_NEW_ID: [MessageHandler((Filters.text), tracking_reply)],
        },
        fallbacks=[CommandHandler("cancel", cancel_conversation)]
    )

    # Register handlers
    dispatcher.add_handler(tracking_conversation_handler)
    dispatcher.add_handler(CommandHandler("start", start_cmd))
    dispatcher.add_handler(CommandHandler("help", help_cmd))

    # Handle all unknown updates
    dispatcher.add_handler(MessageHandler((), unknown_update))

    dispatcher.add_error_handler(error)

    updater.start_polling()
    logger.info("Bot started")
    updater.idle()


if __name__ == "__main__":
    main()
