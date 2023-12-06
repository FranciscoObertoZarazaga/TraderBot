from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, Message
from telegram.ext import Updater, CommandHandler, CallbackContext
from Config import TELEGRAM_BOT_TOKEN, TELEGRAM_USER_ID
from threading import Thread
from time import sleep
from Trade import Trades


class BotTelegram:
    def __init__(self):
        self.updater = Updater(TELEGRAM_BOT_TOKEN)
        self.dispatcher = self.updater.dispatcher
        self.trades = Trades()
        self.arbitrator = None

        ###COMMANDS###
        self.dispatcher.add_handler(CommandHandler('start', self.start))
        self.dispatcher.add_handler(CommandHandler('help', self.help))
        self.dispatcher.add_handler(CommandHandler('state', self.state))
        self.dispatcher.add_handler(CommandHandler('report', self.getTrades))
        ###END COMMANDS###

        ###MESSAGES###
        ###END MESSAGES###

    def setArbitrator(self, arbitrator):
        self.arbitrator = arbitrator

    def run(self):
        self.updater.start_polling()
        self.updater.idle()

    def stop(self):
        self.updater.stop()

    def state(self, update: Update, _):
        Message.delete(update.message)
        state = self.arbitrator.getLastUpdateMsg()
        if state is not None:
            resp = update.message.reply_text(state)
            Thread(target=self.clean, args=(resp, 20)).start()

    def getTrades(self, update: Update, _):
        Message.delete(update.message)
        trades = str(self.trades)
        resp = update.message.reply_text(trades)
        Thread(target=self.clean, args=(resp, 60)).start()

    def start(self, update: Update, context: CallbackContext):
        new_id = update.message.chat.id
        print('TELEGRAM_ID:', new_id)
        self.help(update, context)

    @staticmethod
    def help(update: Update, _):
        Message.delete(update.message)
        buttons = [
            [
                KeyboardButton('/state')
            ],
            [
                KeyboardButton('/report')
            ]
        ]

        keyboard_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)

        msg = 'Welcome'
        update.message.reply_text(msg, reply_markup=keyboard_markup)

    def notify(self, msg):
        self.updater.bot.send_message(TELEGRAM_USER_ID, msg)

    @staticmethod
    def clean(msg, t=60):
        sleep(t)
        Message.delete(msg)
