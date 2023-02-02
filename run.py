import logging
from typing import Optional, Tuple

from telegram import Chat, ChatMember, ChatMemberUpdated, Update, ReplyKeyboardMarkup
from telegram.ext import (Application,
                          MessageHandler,
                          ChatMemberHandler,
                          CommandHandler,
                          filters,
                          ContextTypes,
                          PicklePersistence,
                          ConversationHandler)

import logic



logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

EMAIL, PASSWORD, ACCESS = 0, 1, 2

HELLO_TEXT = """
Добрый день. Вас приветствует бот Перемен.

⚠️ Внимательно знакомьтесь с инструкцией перед регистрацией.

Её можно найти по ссылке: https://eraperemen.info/wp-content/uploads/2022/12/instrukcziya.pdf


⚠️ Избегайте распространенных ошибок

1. Какая у вас почта в бусти не важно.
2. Для того что бы получить доступ на сайт вам необходимо ЧЕТКО следовать описанным ниже шагам;
2.1. Оплата на Boosty
2.2. Попадаете в группу
2.3. Находите бота в группе или по ссылке https://t.me/vremya_peremen_admin_bot
2.4. Нажимаете зарегистрироваться, вводите почту (не обязательно с Boosty),
2.5. Придумываете свой пароль
2.6. Поздравляю ⭐️ Вы зарегистрированы на сайте eraperemen.info

⚠️ Если не сработало

Выйди из чата и снова зайти. Проделать все что описано выше еще раз
"""

PASSWORD_TEXT = """
🔐 Напишите ваш пароль. Для отмены нажмите или пропишите /cancel.

💭 Придумайте надежный пароль (123456 не подойдет😊). После вы сможете восстановить его на сайте.
"""

EMAIL_TEXT = """
✉️ Напишите ваш email

Для отмены действия регистрации нажмите или пропишите  /cancel

💭 E-mail может быть любым. Не обязательно тот, что вы указали на Boosty. С помощью этой почты, по окончанию регистрации, вы сможете войти на сайт.
"""

EMAIL_TEXT_CHECK = """
✉️ Напишите ваш email для проверки доступа

💭 Вы должны быть зарегистрированы на сайте и должна быть оплачена подписка. Введите вашу почту и вы получите доступ в группу.
"""

HELP_TEXT = """
🔧 Если у Вас возникли какие-то проблемы обратитесь в поддержку в телеграмм @eraperementest

💭Хотим обратить ваше внимание что мы пока находимся на стадии тестирования нового сервиса. Будем благодарны за отзывы и понимание.
"""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Приветствует пользоателя и создаёт меня для ссылки на чаты."""
    reply_markup = ReplyKeyboardMarkup([['/access - Получение доступа к группам.'],
                                        ['/registration - Регистрация на сайте.'],
                                        ['/help - Помощь с ботом.'],])

    await update.message.reply_text(text=HELLO_TEXT, reply_markup=reply_markup)


async def registration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected FIO and asks for a education."""
    user_data = context.user_data
    user = update.message.from_user
    user_data[user.id] = {}
    await update.message.reply_text(
        text=EMAIL_TEXT,
    )
    return EMAIL


async def email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохраняет эмейл."""
    user = update.message.from_user
    user_data = context.user_data
    user_data[user.id].update({'email': update.message.text})

    logger.info("name of %s: %s", user.first_name, update.message.text)
    await update.message.reply_text(
        text=PASSWORD_TEXT,
    )

    return PASSWORD


async def password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохраняет пароль."""
    user = update.message.from_user
    user_data = context.user_data
    password = update.message.text
    email = user_data[user.id]['email']

    # тут создание пользователя бусти
    if logic.check_user(email):
        await update.message.reply_text(
            "Вы уже зарегистрированы.",
        )
        return ConversationHandler.END

    # !!! Проверка доступа пользователя !!!
    info_1 = await context.bot.get_chat_member(chat_id=-1001869016733, user_id=user.id)
    info_2 = await context.bot.get_chat_member(chat_id=-1001811351703, user_id=user.id)
    info_3 = await context.bot.get_chat_member(chat_id=-1001634731374, user_id=user.id)
    print(info_1.status, info_2.status, info_3.status)
    if info_1.status != 'member' and info_2.status != 'member' and info_3.status != 'member':
        await update.message.reply_text(
            "Вы не находитесь ни в одной из групп. У вас нет доступа к сайту.",
        )
        return ConversationHandler.END

    if info_1.status == 'member' or info_1.status == 'administrator': # 1$
        access = 1
    if info_2.status == 'member' or info_1.status == 'administrator': # 35$
        access = 2
    if info_3.status == 'member' or info_1.status == 'administrator': # 100$
        access = 3

    logic.create_user(email, password, user.id)
    # !!! Конец проверки !!!
    logic.create_user_subscribe_boosty(email, access)
    logger.info("email of %s: %s", user.first_name, update.message.text)
    await update.message.reply_text(
        f"✅ Регистрация окончена\nВаш аккаунт создан\nEmail:{email}\nPassword:{password}\nТеперь перейдите на наш сайт eraperemen.info и получите доступ к закрытому разделу.\n⭐️ Приятного пользования",)
    user_data[user.id] = {}
    return ConversationHandler.END


def extract_status_change(chat_member_update: ChatMemberUpdated) -> Optional[Tuple[bool, bool]]:
    """Takes a ChatMemberUpdated instance and extracts whether the 'old_chat_member' was a member
    of the chat and whether the 'new_chat_member' is a member of the chat. Returns None, if
    the status didn't change.
    """
    status_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get("is_member", (None, None))

    if status_change is None:
        return None

    old_status, new_status = status_change
    was_member = old_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (old_status == ChatMember.RESTRICTED and old_is_member is True)
    is_member = new_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (new_status == ChatMember.RESTRICTED and new_is_member is True)

    return was_member, is_member


async def track_chats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Tracks the chats the bot is in."""
    result = extract_status_change(update.my_chat_member)
    if result is None:
        return
    was_member, is_member = result

    # Let's check who is responsible for the change
    cause_name = update.effective_user.full_name

    # Handle chat types differently:
    chat = update.effective_chat
    if chat.type == Chat.PRIVATE:
        if not was_member and is_member:
            logger.info("%s started the bot", cause_name)
            context.bot_data.setdefault("user_ids", set()).add(chat.id)
        elif was_member and not is_member:
            logger.info("%s blocked the bot", cause_name)
            context.bot_data.setdefault("user_ids", set()).discard(chat.id)
    elif chat.type in [Chat.GROUP, Chat.SUPERGROUP]:
        if not was_member and is_member:
            logger.info("%s added the bot to the group %s", cause_name, chat.title)
            context.bot_data.setdefault("group_ids", set()).add(chat.id)
        elif was_member and not is_member:
            logger.info("%s removed the bot from the group %s", cause_name, chat.title)
            context.bot_data.setdefault("group_ids", set()).discard(chat.id)
    else:
        if not was_member and is_member:
            logger.info("%s added the bot to the channel %s", cause_name, chat.title)
            context.bot_data.setdefault("channel_ids", set()).add(chat.id)
        elif was_member and not is_member:
            logger.info("%s removed the bot from the channel %s", cause_name, chat.title)
            context.bot_data.setdefault("channel_ids", set()).discard(chat.id)


async def show_chats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows which chats the bot is in"""
    user_ids = ", ".join(str(uid) for uid in context.bot_data.setdefault("user_ids", set()))
    group_ids = ", ".join(str(gid) for gid in context.bot_data.setdefault("group_ids", set()))
    channel_ids = ", ".join(str(cid) for cid in context.bot_data.setdefault("channel_ids", set()))
    text = (
        f"@{context.bot.username} is currently in a conversation with the user IDs {user_ids}."
        f" Moreover it is a member of the groups with IDs {group_ids} "
        f"and administrator in the channels with IDs {channel_ids}."
    )
    await update.effective_message.reply_text(text)


async def greet_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Greets new users in chats and announces when someone leaves"""
    result = extract_status_change(update.chat_member)
    if result is None:
        return
    chat = update.effective_chat
    user = update.chat_member.chat.id


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Действие отменено."
    )

    return ConversationHandler.END


async def access(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало проверки доступа."""
    await update.message.reply_text(
        text=EMAIL_TEXT_CHECK,
    )
    return ACCESS


async def links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверка email."""
    email = update.message.text
    user = update.message.from_user
    if logic.check_tg_id_in_db(email): # Если telegram_id пользователь есть в дб
        access = logic.check_user_category_website_by_subscription(user.id)
    elif logic.check_user(email): # Проверка есть ли вообще такой пользователь
        logic.add_user_tg(email, user.id) # Добавить пользователю tg_id
        access = logic.check_user_category_website_by_subscription(user.id) # Проверка доступа по tg_id
    else:
        await update.message.reply_text(
            "У Вас нет доступа. Обратитесь в поддержку.",
        )
        return ConversationHandler.END

    if access == 1: # 1$
        link = await context.bot.create_chat_invite_link(chat_id=-1001869016733,
                                                         member_limit=1,)
        await update.message.reply_text(text=f"Чат 1$ {link['invite_link']}")
    if access == 2: # 35$
        link = await context.bot.create_chat_invite_link(chat_id=-1001811351703,
                                                         member_limit=1,)
        await update.message.reply_text(text=f"Чат 15$ {link['invite_link']}")
    if access == 3: # 100$
        link_3 = await context.bot.create_chat_invite_link(chat_id=-1001634731374,
                                                           member_limit=1,)
        link_2 = await context.bot.create_chat_invite_link(chat_id=-1001811351703,
                                                           member_limit=1,)
        link_1 = await context.bot.create_chat_invite_link(chat_id=-1001869016733,
                                                           member_limit=1,)
        await update.message.reply_text(text=f"Чат 100$ {link_3['invite_link']}\nЧат 35$ {link_2['invite_link']}\nЧат 1$ {link_1['invite_link']}")

    return ConversationHandler.END


async def clean_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запуск проверки пользователей и бан в случае истечения подписки."""
    user = update.message.from_user
    context.job_queue.run_repeating(alarm, 3600, chat_id=user.id) # !!!!!!


async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the alarm message."""
    all_id = logic.take_all_id()
    print(all_id)
    count = 0
    for i in all_id:
        print(all_id)
        subscriptions = logic.check_subscription_website_by_date(i)
        for subscription in subscriptions:
            # !!! Проверка доступа пользователя !!!
            try:
                info_1 = await context.bot.get_chat_member(chat_id=-1001869016733, user_id=i)
                info_2 = await context.bot.get_chat_member(chat_id=-1001811351703, user_id=i)
                info_3 = await context.bot.get_chat_member(chat_id=-1001634731374, user_id=i)
                if subscription[0] == '712':
                    if subscription[1] == 0:
                        if info_1.status == 'member':
                            if logic.is_user_boosty(i):
                                email = logic.take_user_email_by_id(i)
                                logic.create_user_subscribe_boosty(email, 1)
                            else:
                                count += 1
                                await context.bot.ban_chat_member(chat_id=-1001869016733, user_id=i, until_date=1)
                elif subscription[0] == '873':
                    if subscription[1] == 0:
                        if info_2.status == 'member':
                            if logic.is_user_boosty(i):
                                email = logic.take_user_email_by_id(i)
                                logic.create_user_subscribe_boosty(email, 2)
                            else:
                                await context.bot.ban_chat_member(chat_id=-1001811351703, user_id=i, until_date=1)
                                count += 1
                else:
                    if subscription[1] == 0:
                        if info_3.status == 'member':
                            if logic.is_user_boosty(i):
                                email = logic.take_user_email_by_id(i)
                                logic.create_user_subscribe_boosty(email, 3)
                            else:
                                count += 1
                                await context.bot.ban_chat_member(chat_id=-1001869016733, user_id=i, until_date=1)
                                await context.bot.ban_chat_member(chat_id=-1001811351703, user_id=i, until_date=1)
                                await context.bot.ban_chat_member(chat_id=-1001634731374, user_id=i, until_date=1)
            except Exception as e:
                print(e)
            # !!! Конец проверки !!!
    chat_id = context.job.chat_id
    await context.bot.send_message(chat_id=chat_id, text=f'Забанено людей без подписок: {count}')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text=HELP_TEXT)


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    persistence = PicklePersistence(filepath="conversationbot")
    application = Application.builder().token("5933770954:AAEpoucz37GNQ-t8jCeGBnyNrSKCGtWCH_I").persistence(persistence).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('start_ban_users', clean_groups))
    # Keep track of which chats the bot is in
    application.add_handler(ChatMemberHandler(track_chats, ChatMemberHandler.MY_CHAT_MEMBER))
    application.add_handler(CommandHandler("show_chats", show_chats))

    # Handle members joining/leaving chats.
    application.add_handler(ChatMemberHandler(greet_chat_members, ChatMemberHandler.CHAT_MEMBER))

    reg_handler = ConversationHandler(
        entry_points=[CommandHandler("registration", registration)],
        states={
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, email)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, password)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(reg_handler)

    access_handler = ConversationHandler(
        entry_points=[CommandHandler("access", access)],
        states={
            ACCESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, links)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(access_handler)

    # Run the bot until the user presses Ctrl-C
    # We pass 'allowed_updates' handle *all* updates including `chat_member` updates
    # To reset this, simply pass `allowed_updates=[]`
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
