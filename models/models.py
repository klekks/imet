import peewee
from datetime import datetime, timedelta
from os.path import dirname


db = peewee.SqliteDatabase(dirname(__file__) + "/global.db")


class Page(peewee.Model):
    id = peewee.AutoField()
    text = peewee.TextField(null=True, default="")

    @staticmethod
    def create_page(id, text="") -> 'Page':
        page = Page.create(id=id, text=text)
        return page

    class Meta:
        database = db


class User(peewee.Model):
    id = peewee.BigIntegerField(unique=True, primary_key=True)
    username = peewee.CharField(max_length=64)
    first_name = peewee.CharField(max_length=64)
    last_name = peewee.CharField(max_length=64, default="", null=True)
    current_page = peewee.ForeignKeyField(Page, null=True)
    user_group = peewee.CharField(max_length=32, default="")

    @staticmethod
    def user_in(uid: int, first_name: str, last_name: str, username: str) -> ('User', datetime):
        try:
            user = User.select(User).where(User.id == uid).get()
            #account = Account.select(Account).join(User).where(User.id == uid).get()
            #if account.blocked:
            #    return account.unblocking_date
            #else:
            #    Event.create(account=account)

            #if Event.select(Event).join(Account).join(User).where(User.id==user.id).where(Account.user==user).count() > 100:
            #    account.blocked = True
            #    account.unblocking_date = datetime.now() + timedelta(hours=12)
            #    account.save()
            #    return account.unblocking_date
            return user

        except peewee.DoesNotExist:
            userid = User.create(id=uid, username=username, first_name=first_name)
            if last_name:
                user.last_name = last_name
                user.save()
            account = Account.create(user=user)

        return user

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "username": self.username,
            "current_page": self.current_page
        }

    class Meta:
        database = db


class Button(peewee.Model):
    page = peewee.ForeignKeyField(Page)
    name = peewee.CharField(max_length=16)
    next_page = peewee.ForeignKeyField(Page, default=None)
    action = peewee.CharField(max_length=32, null=True, default="")

    @staticmethod
    def create_button(page, name, next_page_id):
        try:
            Button.select(Button).join(Page).where(Page.id == page).where(Button.name == name).get()
            return
        except peewee.DoesNotExist:
            pass

        try:
            existed_page = Page.select(Page).where(Page.id == page).get()
        except peewee.DoesNotExist:
            existed_page = Page.create_page(page)
        try:
            next_page = Page.select(Page).where(Page.id == next_page_id).get()
        except peewee.DoesNotExist:
            next_page = Page.create_page(next_page_id)

        print(name, existed_page, next_page)
        button = Button.create(page=existed_page, name=name, next_page=next_page)

        return button

    @staticmethod
    def on_click(page, name) -> (Page, None, list['Button']):
        try:
            b = Button.select(Button).where(Button.page.id == page).where(Button.name == name).get()
        except peewee.DoesNotExist:
            return None

        page = b.next_page

        if not page:
            return None
        else:
            buttons = Button.select(Button).where(Button.page.id == page.id)[:]
            return buttons


    def to_dict(self):
        return {
            "page": self.page.id,
            "name": self.name,
            "next_page": self.next_page.id,
            "action": self.action
        }


    class Meta:
        database = db


class Account(peewee.Model):
    user = peewee.ForeignKeyField(User)
    blocked = peewee.BooleanField(default=False)
    unblocking_date = peewee.DateTimeField(null=True)

    class Meta:
        database = db


class Event(peewee.Model):
    account = peewee.ForeignKeyField(Account)
    date = peewee.DateTimeField(default=datetime.now())
    type = peewee.CharField(max_length=16, default="message")

    class Meta:
        database = db


class WaitEvent(peewee.Model):
    user = peewee.ForeignKeyField(User)
    event = peewee.CharField(max_length=16)

    @staticmethod
    def create_wait_event(user: int, event: str):
        user = User.select(User).where(User.id == user).get()
        return WaitEvent.create(user=user, event=event)

    class Meta:
        database = db


db.connect()
db.create_tables([User, Page, Button, Account, Event, WaitEvent])
