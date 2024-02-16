import os

import telebot
from dotenv import load_dotenv

from bot import Bot
from config import Config
from markup import Markup
from repository import Database


def main():
    load_dotenv()
    config = Config(
        bot_id=os.getenv('BOT_ID'),
        bot_partner_link=os.getenv('BOT_PARTNER_LINK'),
        super_admin_id=os.getenv('SUPER_ADMIN_ID'),
        super_admin_name=os.getenv('SUPER_ADMIN_NAME'),
    )
    database = Database(
        database_user=os.getenv('DATABASE_USER'),
        database_name=os.getenv('DATABASE_NAME'),
        database_host=os.getenv('DATABASE_HOST'),
        database_port=int(os.getenv('DATABASE_PORT')),
        database_password=os.getenv('DATABASE_PASSWORD'),
        config=config,
    )
    markup = Markup(config=config, database=database)
    app = Bot(config=config, database=database, bot=telebot.TeleBot(os.getenv('BOT_TOKEN')), markup=markup)
    app.bot.infinity_polling()


if __name__ == '__main__':
    main()
