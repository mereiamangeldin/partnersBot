import os

import telebot
from dotenv import load_dotenv
from flask import Flask, request

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
    flaskApp = Flask(__name__)

    @flaskApp.route('/' + os.getenv('BOT_TOKEN'), methods=['POST'])
    def getMessage():
        app.bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
        return "!", 200

    app.bot.remove_webhook()
    app.bot.set_webhook(url='https://partnerbot.herokuapp.com/'+os.getenv('BOT_TOKEN'))

    flaskApp.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))


if __name__ == '__main__':
    main()
