from telebot import types

from model import NumericVariable


class Markup:
    def __init__(self, config, database):
        self.config = config
        self.database = database

    def user_home_markup(self, language: str):
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        markup.add(
            self.config.user_home_menu[language]['earn_money'],
            self.config.user_home_menu[language]['partners'],
            self.config.user_home_menu[language]['balance'],
            self.config.user_home_menu[language]['language'],
        )
        return markup

    def admin_home_markup(self):
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        markup.add(
            self.config.admin_home_menu['add_admin'],
            self.config.admin_home_menu['add_channel'],
            self.config.admin_home_menu['delete_admin'],
            self.config.admin_home_menu['delete_channel'],
            self.config.admin_home_menu['view_channel_statistics'],
            self.config.admin_home_menu['view_bot_statistics'],
            self.config.admin_home_menu['change_variable'],
            self.config.admin_home_menu['send_message'],
        )
        return markup

    def earn_money_markup(self, language):
        numericVariable = self.database.session.query(NumericVariable).get(1)
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton(
            f'{self.config.user_earn_money_menu[language]["invite_friend"]}: {numericVariable.invite_friend_price} Сом',
            callback_data='invite_friend'))
        markup.add(types.InlineKeyboardButton(
            f'{self.config.user_earn_money_menu[language]["join_channel"]}: {numericVariable.join_channel_price} Сом',
            callback_data='join_channel'))
        markup.add(types.InlineKeyboardButton(
            f'{self.config.user_earn_money_menu[language]["view_post"]}: {numericVariable.view_post_price} Сом',
            callback_data='view_post'))

        return markup

    def withdraw_markup(self, message):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(message, callback_data='withdraw'))
        return markup

    def change_variables_markup(self):
        numericVariable = self.database.session.query(NumericVariable).get(1)
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add(
            f'{self.config.admin_change_variable["invite_friend"]}: {numericVariable.invite_friend_price} сом',
            f'{self.config.admin_change_variable["join_channel"]}: {numericVariable.join_channel_price} сом',
            f'{self.config.admin_change_variable["view_post"]}: {numericVariable.view_post_price} сом',
            f'{self.config.admin_change_variable["min_withdrawal_amount"]}: {numericVariable.min_withdrawal_amount} сом',
            f'{self.config.admin_change_variable["min_invited_friends"]}: {numericVariable.min_invited_friends} человек',
            self.config.admin_inner_vars['cancel'],
        )
        return markup

    def cancel_markup(self):
        return types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True).add(
                                         self.config.admin_inner_vars['cancel'])
