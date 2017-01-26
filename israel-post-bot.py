#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Israel Post Telegram Bot - Track your packages via Telegram

Make sure you have your bot token saved in a file named 'token'.
Github: https://github.com/LiranV/israel-post-bot
"""

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import json
import logging
import urllib.request
from collections import namedtuple

TRACKING_URL = "http://www.israelpost.co.il/itemtrace.nsf/trackandtraceJSON?OpenAgent&lang=en&itemcode={}"
TOKEN_FILE = "token"
HELP_MENU = None
commands = {}
command_tuple = namedtuple("CommandTuple", ("callback", "info", "usage"))

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def start(bot, update):
    logger.info("Received 'start' from user '{}'".format(update.message.from_user["id"]))
    start_message = "Israel Post Telegram Bot at your service!\n" \
                    + "For help type '/help'"
    bot.sendMessage(chat_id=update.message.chat_id, text=start_message)


def track(bot, update, args):
    if len(args) != 1:
        bot.sendMessage(chat_id=update.message.chat_id, text="Please refer to '/help track'")
        return
    tracking_id = args[0]
    logger.info("Tracking package {}, requested by user '{}'".format(tracking_id,
                update.message.from_user["id"]))
    tracking_info = get_tracking_information(args[0])
    bot.sendMessage(chat_id=update.message.chat_id, text=tracking_info)


def gen_help_menu():
    global commands
    global HELP_MENU
    header = ("Israel Post Telegram Bot\n\n"
              "Available commands:\n")
    message = [header]
    for command in commands:
        message.append("/{} - {}".format(command, commands[command].info))
    HELP_MENU = "\n".join(message)


def help_menu(bot, update, args):
    global HELP_MENU
    global commands
    if not args:
        bot.sendMessage(chat_id=update.message.chat_id, text=HELP_MENU)
        return
    command_name = args[0]
    if command_name in commands:
        message = "'/{}' takes no arguments".format(command_name)
        if commands[command_name].usage:
            message = "Usage:\n\t{}".format(commands[command_name].usage)
        bot.sendMessage(chat_id=update.message.chat_id, text=message)
    else:
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="'/{}' is an unknown command".format(command_name))


def unknown(bot, update):
    message = ("Sorry, I didn't understand that command.\n"
               "Please refer to '/help' for available commands.")
    bot.sendMessage(chat_id=update.message.chat_id, text=message)


def error(bot, update, error):
    logger.warn("Update '{}' caused error '{}'".format(update, error))


def read_token():
    with open(TOKEN_FILE, 'r') as f:
        token = f.read().strip("\n")
        logger.info("Bot token: {}".format(token))
        return token


def get_tracking_information(tracking_id):
    with urllib.request.urlopen(TRACKING_URL.format(tracking_id)) as response:
        data = json.loads(response.read().decode("utf-8"))
    track_info = data["itemcodeinfo"]
    return track_info[:track_info.index("<br>")]


def add_command(dispatcher, name, callback, info, usage="", pass_args=False):
    global commands
    commands[name] = command_tuple(callback, info, usage)
    dispatcher.add_handler(CommandHandler(name, callback, pass_args=pass_args))


def unknown_message(bot, update):
    message = "I'm sorry but I couldn't understand you.\nYou should probably try to look at '/help'"
    bot.sendMessage(chat_id=update.message.chat_id, text=message)


def main():
    updater = Updater(token=read_token())
    dispatcher = updater.dispatcher

    # Register handlers
    add_command(dispatcher, "start", start, "Display greeting message")
    add_command(dispatcher, "track", track, "Track package", "/track <tracking code>", pass_args=True)
    add_command(dispatcher, "help", help_menu, "Display help", "/help [command]", pass_args=True)

    # Handle all unknown commands
    dispatcher.add_handler(MessageHandler((Filters.command), unknown))

    # Handle all unknown messages
    dispatcher.add_handler(MessageHandler((), unknown_message))

    dispatcher.add_error_handler(error)

    gen_help_menu()
    updater.start_polling()
    logger.info("Bot started")
    updater.idle()

if __name__ == "__main__":
    main()
