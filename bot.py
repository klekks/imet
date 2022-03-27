import telebot
from models.models import Button, Page, User, Account, Event, WaitEvent
import datetime

from json import loads, dumps


telebot.apihelper.ENABLE_MIDDLEWARE = True
bot = telebot.TeleBot("5253201490:AAFEjwiJgHQe_pALCgwcS0Yj4ylRatDQq1Y", parse_mode=None)


def sayhi(message):
    bot.reply_to(message, "Hi!")


def init_ruz(message):
    WaitEvent.create(user=message.from_user, event="ruz_group_wait")


def ruz_markup(message, markup):
    if message.from_user.user_group:
        markup.row(
                message.from_user.user_group
        )


def clear_ruz(message):
    for i in WaitEvent.select(WaitEvent).join(User).where(User == message.from_user):
        i.delete_instance()
        i.save()

    message.from_user.current_page = 1
    message.from_user.save()


def ruz_group_wait(message, events):
    group = message.text

    from requests import get
    import re
    res = get("https://ruz.spbstu.ru/search/groups?q={0}".format(group))

    if res.status_code != 200:
        return

    data = re.search(r"<script>\s*window\.__INITIAL_STATE__ = (.*)\s*;\s*</script>", res.text).group(1)
    data = loads(data)
    group_id = data["searchGroup"]["data"][0]["id"]
    group_name = data["searchGroup"]["data"][0]["name"]

    message.from_user.user_group = group_name
    message.from_user.save()

    res = get("https://ruz.spbstu.ru/api/v1/ruz/scheduler/{0}".format(group_id))

    if res.status_code != 200:
        return

    ruz = loads(res.text)
    today = datetime.datetime.today().strftime("%Y-%m-%d")
    week = list(ruz['days'])

    message.from_user.current_page = Page.select(Page).where(Page.id == 1).get()
    message.from_user.save()
    reply_markup = gen_markup(message.from_user.current_page.id)
    try:
        ruz_for_today = list(filter(lambda day: day['date'] == today, week))[0]
    except:
        bot.send_message(message.chat.id, "Нет пар на сегодня", reply_markup=reply_markup)
        return

    lessons = ruz_for_today['lessons']

    ruz = ["Расписание для {1} на {0}:".format(today, group_name), ]

    for i in lessons:
        ruz.append(
         "📍 {0}: {1} ({2}, ауд. {3})".format(i['time_start'], i['subject_short'], i['auditories'][0]['building']['name'], i['auditories'][0]['name'])
        )

    for i in events:
        i.delete_instance()

    for msg in ruz:
        bot.send_message(message.chat.id, msg, reply_markup=reply_markup)


ACTIONS = {
    "sayhi": sayhi,
    "init_ruz": init_ruz,
    "ruz_group_wait": ruz_group_wait,
    'clear_ruz': clear_ruz
}

UPDATE_ACTION = {
    "init_ruz": ruz_markup
}


@bot.middleware_handler(update_types=['message'])
def load_user(bot_instance, message):
    message.from_user = User.user_in(
        message.from_user.id,
        message.from_user.first_name,
        message.from_user.last_name,
        message.from_user.username
    )
    message.blocked = False
    if type(message.from_user) == datetime.datetime:
        message.blocked = True
        return bot.reply_to(message, "You are banned until " + str(message.from_user))

    cnt = Event.select(Event).join(Account).join(User).where(User.id==message.from_user.id).where(Account.user==message.from_user).count()
    print(message.from_user.to_dict())
    print("Events: ", cnt)


@bot.middleware_handler(update_types=['message'])
def check_if_wait(bot_instance, message):
    msgs = WaitEvent.select(WaitEvent).where(WaitEvent.user == message.from_user)[:]

    if not msgs:
        message.replied = False
    else:
        try:
            message.replied = True
            ACTIONS[msgs[0].event](message, msgs)
        except:
            for msg in msgs:
                msg.delete_instance()
                msg.save()
            message.replied = False


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message: telebot.types.Message):
    try:
        message.from_user.current_page = Page.select(Page).where(Page.id == 1).get()
        message.from_user.save()
    except:
        bot.send_message(message.chat.id, "MAMMAMIA")

    markup = gen_markup(1)

    bot.send_message(message.chat.id, message.from_user.current_page.text, reply_markup=markup)


@bot.message_handler(commands=['addbutton'])
def add_button(message: telebot.types.Message):
    command, page, button, *next_page = message.text.split(" ")

    if not next_page: next_page = None
    else: next_page = next_page[0]

    b = Button.create_button(page, button, next_page)

    bot.reply_to(message, "{0} : {1}".format(b.page, b.name))


@bot.message_handler(func=lambda m: not m.replied)
def echo_all(message: telebot.types.Message):
    try:
        print(message.from_user.to_dict())
        pressed_button = Button.select(Button, Page).join(Page).where(Page.id == message.from_user.current_page.id)\
                                                         .where(Button.name == message.text).get()
        if pressed_button.next_page.id:
            markup = gen_markup(pressed_button.next_page.id)
            message.from_user.current_page = pressed_button.next_page
            message.from_user.save()
            if pressed_button.action:
                ACTIONS[pressed_button.action](message)
                if pressed_button.action in UPDATE_ACTION:
                    UPDATE_ACTION[pressed_button.action](message, markup)
            bot.send_message(message.chat.id, message.from_user.current_page.text, reply_markup=markup)
        else:
            ACTIONS[pressed_button.action](message)
    except:
        print('trouble')
        bot.reply_to(message, message.text)


def gen_markup(page):
    items = Button.select(Button).join(Page).where(Page.id == page)[:]
    markup = telebot.types.ReplyKeyboardMarkup()

    for i in range(0, len(items), 2):
        if i + 1 < len(items):
            markup.row(
                telebot.types.KeyboardButton(items[i].name),
                telebot.types.KeyboardButton(items[i+1].name),
            )
        else:
            markup.row(
                telebot.types.KeyboardButton(items[i].name)
            )
    return markup


bot.infinity_polling()
