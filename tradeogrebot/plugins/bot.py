import time
import tradeogrebot.emoji as emo
import tradeogrebot.labels as lbl

from enum import auto
from threading import Thread
from tradeogrebot.plugin import TradeOgreBotPlugin
from tradeogrebot.config import ConfigManager as Cfg
from telegram import ParseMode, ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import RegexHandler, ConversationHandler, MessageHandler, \
    Filters, CommandHandler, CallbackQueryHandler


class Bot(TradeOgreBotPlugin):

    # Conversation handler states
    BOT_CHOOSE = auto()
    BOT_FEEDBACK = auto()
    BOT_REMOVE_AC = auto()

    def get_handlers(self):
        return [self._get_bot_handler(),
                self._get_shutdown_handler(),
                self._get_help_handler(),
                self._get_remove_acc_callback_handler()]

    def _get_bot_handler(self):
        return ConversationHandler(
            entry_points=[RegexHandler(f"^({lbl.BTN_BOT})$", self._bot)],
            states={
                self.BOT_CHOOSE:
                    [RegexHandler(f"^({lbl.BTN_HELP})$", self._bot_help),
                     RegexHandler(f"^({lbl.BTN_SHUTDOWN})$", self._bot_shutdown),
                     RegexHandler(f"^({lbl.BTN_REMOVE_AC})$", self._bot_remove_account),
                     RegexHandler(f"^({lbl.BTN_FEEDBACK})$", self._bot_feedback),
                     RegexHandler(f"^({lbl.BTN_BACK})$", self.back)],
                self.BOT_FEEDBACK:
                    [RegexHandler(f"^({lbl.BTN_BACK})$", self.back),
                     MessageHandler(Filters.text, self._bot_feedback_save)]
            },
            fallbacks=[MessageHandler(Filters.text, self.back)],
            allow_reentry=True)

    def _get_remove_acc_callback_handler(self):
        return CallbackQueryHandler(
            self._callback_remove_ac,
            pattern="^(remove-acc-yes|remove-acc-no)$")

    def _get_shutdown_handler(self):
        return CommandHandler(
            "shutdown", self._bot_shutdown,
            filters=Filters.user(user_id=Cfg.get("admin_id")))

    def _get_help_handler(self):
        return CommandHandler("help", self._bot_help)

    @TradeOgreBotPlugin.add_user
    @TradeOgreBotPlugin.send_typing_action
    def _bot(self, bot, update):
        update.message.reply_text(
            text="Choose an option",
            reply_markup=self._keyboard_bot(update))

        return self.BOT_CHOOSE

    # TODO: Update this with proper info
    @TradeOgreBotPlugin.send_typing_action
    def _bot_help(self, bot, update):
        help_msg = f"{emo.STARS} *Welcome to TradeOgre-Bot* {emo.STARS}\n" \
                   f"This bot is open source. You can take a look at the " \
                   f"source code [here](https://github.com/Endogen/Telegr" \
                   f"am-TradeOgre-Bot) or drop me a message if you have a" \
                   f"ny questions: @endogen\n\nThis description is just a" \
                   f" very short version of the documentation you can fin" \
                   f"d in the link above.\n\n{emo.BULLETPOINT} *Security*" \
                   f"\nEvery data saved on our server is encrypted. If yo" \
                   f"u choose to save your API keys on the sever, there i" \
                   f"s no way for us to know that, or even read them.\n\n" \

        update.message.reply_text(
            text=help_msg,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboard_main(),
            disable_web_page_preview=True)

        return ConversationHandler.END

    @TradeOgreBotPlugin.send_typing_action
    def _shutdown(self, bot, update):
        self.updater.stop()
        self.updater.is_idle = False

    @TradeOgreBotPlugin.send_typing_action
    def _bot_shutdown(self, bot, update):
        update.message.reply_text(
            text="Shutting down...",
            reply_markup=self.keyboard_main())

        Thread(target=self._shutdown(bot, update)).start()

        time.sleep(5)
        exit("User requested shutdown")

    @TradeOgreBotPlugin.send_typing_action
    def _bot_remove_account(self, bot, update):
        update.message.reply_text(
            text=f"All your data will be removed from the "
                 f"database. Do you want to proceed?",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self._keyboard_remove_ac_confirm())

    @TradeOgreBotPlugin.send_typing_action
    def _callback_remove_ac(self, bot, update):
        query = update.callback_query
        user_id = query.message.chat_id

        if query.data == "remove-acc-no":
            bot.edit_message_text(
                text=f"`{query.message.text}`\n"
                     f"{emo.CANCEL} *Canceled*",
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                parse_mode=ParseMode.MARKDOWN)

            return

        self.db.remove_user(user_id)

        bot.edit_message_text(
            text=f"{query.message.text}\n"
                 f"{emo.FINISH} *All data removed*",
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            parse_mode=ParseMode.MARKDOWN)

    @TradeOgreBotPlugin.send_typing_action
    def _bot_feedback(self, bot, update):
        help_msg = "Enter your feedback"

        update.message.reply_text(
            text=help_msg,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboard_back())

        return self.BOT_FEEDBACK

    @TradeOgreBotPlugin.send_typing_action
    def _bot_feedback_save(self, bot, update):
        feedback = update.message.text

        user = update.message.from_user
        if user.username:
            name = user.username
        else:
            name = user.first_name

        bot.send_message(Cfg.get("admin_id"), f"Feedback from @{name}: {feedback}")

        update.message.reply_text(
            text=f"Feedback send, thanks! {emo.TOP}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.keyboard_main())

        return ConversationHandler.END

    def _keyboard_bot(self, update):
        buttons = [
            KeyboardButton(lbl.BTN_FEEDBACK),
            KeyboardButton(lbl.BTN_HELP),
            KeyboardButton(lbl.BTN_REMOVE_AC)
        ]

        if update.message.from_user.id == Cfg.get("admin_id"):
            buttons.append(KeyboardButton(lbl.BTN_SHUTDOWN))

        return ReplyKeyboardMarkup(
            self.build_menu(buttons, n_cols=2, footer_buttons=[KeyboardButton(lbl.BTN_BACK)]),
            resize_keyboard=True)

    def _keyboard_remove_ac_confirm(self):
        keyboard_markup = [[
            InlineKeyboardButton("Yes", callback_data="remove-acc-yes"),
            InlineKeyboardButton("No", callback_data="remove-acc-no")]]

        return InlineKeyboardMarkup(keyboard_markup)
