import datetime
import time

from sqlalchemy import func
from telebot import TeleBot, types

from config import Config
from markup import Markup
from model import User, Admin, NumericVariable, Partner, Subscription
from repository import Database


class Bot:
    def __init__(self, database: Database, config: Config, bot: TeleBot, markup: Markup):
        self.database = database
        self.config = config
        self.bot = bot
        self.markup = markup
        self.register_handlers()

    def get_numeric_variables(self) -> NumericVariable:
        n = self.database.session.query(NumericVariable).get(1)
        return n

    def register_handlers(self):

        @self.bot.message_handler(commands=['start'])
        def start(message):
            inviting_user_id = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
            user = self.database.session.query(User).get(str(message.from_user.id))
            admin = self.database.session.query(Admin).get(str(message.from_user.id))
            if not user and not admin:
                invited_from_id = '0'
                if inviting_user_id:
                    inviting_user = self.database.session.query(User).get(inviting_user_id)
                    if inviting_user:
                        numeric_variable = self.get_numeric_variables()
                        inviting_user.balance += numeric_variable.invite_friend_price
                        self.database.session.commit()
                        invited_from_id = inviting_user.id
                        if inviting_user.language == self.config.language_RU:
                            self.bot.send_message(chat_id=inviting_user.id,
                                                  text=f"Пользователь: {message.from_user.username}\nУспешно зарегистрировался по вашей ссылке!\n\n<i>Вам начисляется: {numeric_variable.invite_friend_price} сом</i>",
                                                  parse_mode='HTML')
                        elif inviting_user.language == self.config.language_KG:
                            self.bot.send_message(chat_id=inviting_user.id,
                                                  text=f"Колдонуучу: {message.from_user.username}\nСиздин шилтемеңиз аркылуу ийгиликтүү катталды!\n\n<i>Сизге чегерилет: {numeric_variable.invite_friend_price} сом</i>",
                                                  parse_mode='HTML')

                user = User(id=str(message.from_user.id), username=message.from_user.username,
                            invited_from_id=str(invited_from_id))
                self.database.session.add(user)
                self.database.session.commit()

            if admin:
                welcome_message = "Добро пожаловать Админ!"
                markup = self.markup.admin_home_markup()
            else:
                user = self.database.session.query(User).get(str(message.from_user.id))
                welcome_message = "👋Привет!\n\nЕсли вы читаете это, значит, вы такой же бизнесмен, как и я, который хочет зарабатывать деньги!\nУ этого бота очень простая система: каналы-спонсоры платят боту за рекламу, а бот платит вам за подписку на эти каналы!\n\nВывести деньги из бота можно на: Visa/Mastercard и другие." if user.language == self.config.language_RU else "👋Салам!\n\nЭгер сиз муну окуп жатсаңыз, демек сиз мендей акча тапкысы келген бизнесменсиз!\nБул бот абдан жөнөкөй системага ээ: демөөрчү каналдар жарнама үчүн ботко акча төлөйт, ал эми бот бул каналдарга жазылганыңыз үчүн төлөйт!\n\nСиз боттон акча ала аласыз: Visa/Mastercard жана башкалар."
                markup = self.markup.user_home_markup(user.language)

            self.bot.send_message(message.chat.id, welcome_message, reply_markup=markup)

        def earn_money_options(user):
            self.bot.send_message(user.id,
                                  "Выберите способ заработка" if user.language == self.config.language_RU
                                  else "Акча табуунун жолун тандаңыз",
                                  reply_markup=self.markup.earn_money_markup(user.language))

        def share_partner_link(user):
            numericVariable = self.get_numeric_variables()
            invited_users_num = self.database.session.query(User).filter_by(invited_from_id=str(user.id)).count()
            share_message = f"🗣Пригласи своих друзей и получи за это деньги\n\n" \
                            f"Отправь друзьям данную ссылку:\n{self.config.bot_partner_link + user.id}\n" \
                            f"<b>{numericVariable.invite_friend_price} сом за каждого приглашенного друга</b>\n" \
                            f"<i>Чтобы деньги зачислились, приглашенные друзья должны запустить бот</i>\n\n" \
                            f"▪️<b>Количество приглашенных друзей</b>: {invited_users_num}\n" \
                            f"▪️<b>Заработано денег</b>: {invited_users_num * numericVariable.invite_friend_price}" if user.language == self.config.language_RU \
                else f"🗣Досторуңузду чакырыңыз жана ал үчүн акча алыңыз\n\n" \
                     f"Бул шилтемени досторуңузга жөнөтүңүз:\n{self.config.bot_partner_link + user.id}\n" \
                     f"<b>Ар бир чакырылган дос үчүн {numericVariable.invite_friend_price} сомдон</b>\n" \
                     f"<i>Акча чегерилиши үчүн, чакырылган достор ботту иштетиши керек</i>\n\n" \
                     f"▪️<b>Чакырылган достордун саны</b>: {invited_users_num}\n" \
                     f"▪️<b>Табылган акча</b>: {invited_users_num * numericVariable.invite_friend_price}"

            self.bot.send_message(user.id, share_message, parse_mode='HTML',
                                  reply_markup=self.markup.user_home_markup(user.language))

        def show_balance(user):
            numericVariable = self.get_numeric_variables()
            balance_message = f"<b>Ваш баланс</b>: {user.balance} сом\n\n" \
                              f"<i>Минимальная сумма для снятие денег: {numericVariable.min_withdrawal_amount} сом</i>" if user.language == self.config.language_RU \
                else f"<b>Сиздин балансыңыз</b>: {user.balance} сом\n\n" \
                     f"<i>Акча алуу үчүн минималдуу сумма</i>: {numericVariable.min_withdrawal_amount} сом"
            self.bot.send_message(user.id, balance_message, parse_mode='HTML',
                                  reply_markup=self.markup.withdraw_markup(
                                      'Снять деньги' if user.language == self.config.language_RU else 'Акча алуу'))

        def switch_language(user):
            new_language = self.config.language_KG if user.language == self.config.language_RU else self.config.language_RU
            user.language = new_language
            self.database.session.commit()
            response_message = "Программанын тили кыргызчага өзгөртүлдү🇰🇬" if new_language == self.config.language_KG \
                else "Язык программы сменен на русский язык🇷🇺"
            self.bot.send_message(user.id, response_message,
                                  reply_markup=self.markup.user_home_markup(new_language))

        def admin_send_message(message, admin):
            users = self.database.session.query(User).all()
            active_users = 0
            passive_users = 0
            for u in users:
                try:
                    initial_text = message.text
                    text = initial_text.replace("{username}", u.username)
                    self.bot.send_message(u.id, text)
                    active_users += 1
                except Exception as e:
                    passive_users += 1
            numericVariable = self.get_numeric_variables()
            numericVariable.total_users_amount = len(users)
            numericVariable.active_users_amount = active_users
            numericVariable.passive_users_amount = passive_users
            admin.admin_do_input = False
            admin.admin_input_val = ''
            self.database.session.commit()
            self.bot.send_message(message.chat.id, "Сообщение успешно доставлено пользователям",
                                  reply_markup=self.markup.admin_home_markup())

        def is_number(var):
            if (var[0] == '-' and not str.isdigit(var[1:])) or (
                    not str.isdigit(var) and not var[0] == '-'):
                return False
            return True

        def admin_delete_admin(message, admin):
            if not is_number(message.text):
                self.bot.send_message(message.chat.id, "Введите числовое значение либо нажмите на отменить")
                return
            admin.admin_do_input = False
            deleting_admin = self.database.session.query(Admin).get(message.text)
            self.database.session.delete(deleting_admin)
            self.bot.send_message(message.chat.id, "Процесс выполнен", reply_markup=self.markup.admin_home_markup())

        def admin_new_admin_name(message, admin):
            admin.new_admin_name = message.text
            admin.admin_input_val = self.config.admin_inner_vars['waiting_new_admin_id']
            self.database.session.commit()
            self.bot.send_message(message.chat.id,
                                  "Введите ID нового админа. Чтобы узнать ID: отправьте @имя_пользователя на бот https://t.me/username_to_id_bot",
                                  reply_markup=self.markup.cancel_markup())

        def admin_new_admin_id(message, admin):
            if not is_number(message.text):
                self.bot.send_message(message.chat.id, "Введите числовое значение либо нажмите на отменить")
                return
            exist_admin = self.database.session.query(Admin).get(message.text)
            if exist_admin:
                self.bot.send_message(message.chat.id, "Такой админ уже существует",
                                      reply_markup=self.markup.admin_home_markup())
                return
            new_admin = Admin(id=message.text, name=admin.new_admin_name)
            admin.admin_do_input = False
            admin.new_admin_name = ''
            self.database.session.add(new_admin)
            self.database.session.commit()
            self.bot.send_message(message.chat.id, "Процесс выполнен",
                                  reply_markup=self.markup.admin_home_markup())

        def admin_new_channel_link(message, admin):
            admin.new_channel_link = message.text
            admin.admin_input_val = self.config.admin_inner_vars['waiting_new_channel_id']
            self.database.session.commit()
            self.bot.send_message(message.chat.id,
                                  "Введите ID нового канала. Чтобы узнать ID: отправьте ссылку канала на бот https://t.me/username_to_id_bot",
                                  reply_markup=self.markup.cancel_markup())

        def admin_new_channel_id(message, admin):
            if not is_number(message.text):
                self.bot.send_message(message.chat.id, "Введите числовое значение либо нажмите на отменить")
                return
            exist_channel = self.database.session.query(Partner).get(message.text)
            if exist_channel:
                self.bot.send_message(message.chat.id, "Такой канал уже существует",
                                      reply_markup=self.markup.admin_home_markup())
                return
            channel = Partner(id=message.text, link=admin.new_channel_link)
            self.database.session.add(channel)
            admin.admin_do_input = False
            admin.new_channel_link = ''
            self.database.session.commit()
            self.bot.send_message(message.chat.id, "Процесс выполнен", reply_markup=self.markup.admin_home_markup())

        def admin_delete_channel(message, admin):
            if not is_number(message.text):
                self.bot.send_message(message.chat.id, "Введите числовое значение либо нажмите на отменить")
                return
            admin.admin_do_input = False
            deleting_channel = self.database.session.query(Partner).get(message.text)
            self.database.session.delete(deleting_channel)
            self.database.session.commit()
            self.bot.send_message(message.chat.id, "Процесс выполнен", reply_markup=self.markup.admin_home_markup())

        def admin_change_variable(message, admin, changing_field):
            if not str.isdigit(message.text):
                self.bot.send_message(message.chat.id, "Введите числовое значение либо нажмите на отменить")
                return

            numericVariables = self.get_numeric_variables()
            new_value = int(message.text)
            match changing_field:
                case text if text == self.config.admin_change_variable.get('invite_friend'):
                    numericVariables.invite_friend_price = new_value
                case text if text == self.config.admin_change_variable.get('join_channel'):
                    numericVariables.join_channel_price = new_value
                case text if text == self.config.admin_change_variable.get('view_post'):
                    numericVariables.view_post_price = new_value
                case text if text == self.config.admin_change_variable.get('min_withdrawal_amount'):
                    numericVariables.min_withdrawal_amount = new_value
                case text if text == self.config.admin_change_variable.get('min_invited_friends'):
                    numericVariables.min_invited_friends = new_value
            admin.admin_do_input = False
            self.database.session.commit()
            self.bot.send_message(message.chat.id, "Значение успешно изменено",
                                  reply_markup=self.markup.admin_home_markup())

        @self.bot.message_handler(func=lambda message: True)
        def handle_message(message):
            user = self.database.session.query(User).get(str(message.from_user.id))
            admin = self.database.session.query(Admin).get(str(message.from_user.id))

            if not admin:
                if message.text in self.config.user_home_menu[user.language].values():
                    if user.username != message.from_user.username:
                        user.username = message.from_user.username
                        self.database.session.commit()

                    actions = {
                        self.config.user_home_menu[user.language]['language']: lambda u: switch_language(u),
                        self.config.user_home_menu[user.language]['balance']: lambda u: show_balance(u),
                        self.config.user_home_menu[user.language]['partners']: lambda u: share_partner_link(u),
                        self.config.user_home_menu[user.language]['earn_money']: lambda u: earn_money_options(u),
                    }
                    actions[message.text](user)
                return

            if admin.admin_do_input:
                if message.text == self.config.admin_inner_vars.get('cancel'):
                    admin.admin_do_input = False
                    admin.admin_input_val = ''
                    self.database.session.commit()
                    self.bot.send_message(message.chat.id, "Процесс отменен",
                                          reply_markup=self.markup.admin_home_markup())
                match admin.admin_input_val:
                    case text if text == self.config.admin_inner_vars.get("send_button"):
                        admin_send_message(message=message, admin=admin)
                    case text if text == self.config.admin_inner_vars.get("waiting_deleting_admin_id"):
                        admin_delete_admin(message=message, admin=admin)
                    case text if text == self.config.admin_inner_vars.get("waiting_new_admin_name"):
                        admin_new_admin_name(message=message, admin=admin)
                    case text if text == self.config.admin_inner_vars.get("waiting_new_admin_id"):
                        admin_new_admin_id(message=message, admin=admin)
                    case text if text == self.config.admin_inner_vars.get("waiting_new_channel_link"):
                        admin_new_channel_link(message=message, admin=admin)
                    case text if text == self.config.admin_inner_vars.get("waiting_new_channel_id"):
                        admin_new_channel_id(message=message, admin=admin)
                    case text if text == self.config.admin_inner_vars.get("waiting_deleting_channel_id"):
                        admin_delete_channel(message=message, admin=admin)
                    case changing_field if changing_field in self.config.admin_change_variable.values():
                        admin_change_variable(message=message, admin=admin, changing_field=changing_field)

                return

            if message.text.split(':')[0] in self.config.admin_change_variable.values():
                admin.admin_do_input = True
                admin.admin_input_val = message.text.split(':')[0]
                self.database.session.commit()
                self.bot.send_message(message.chat.id, "Введите значение на которую хотите поменять: ",
                                      reply_markup=self.markup.cancel_markup())

                return

            match message.text:
                case text if text == self.config.admin_inner_vars.get('cancel'):
                    admin.admin_input_val = ''
                    self.database.session.commit()
                    self.bot.send_message(message.chat.id, "Процесс отменен",
                                          reply_markup=self.markup.admin_home_markup())
                case text if text == self.config.admin_home_menu.get('change_variable'):
                    self.bot.send_message(message.chat.id, "Выберите значение",
                                          reply_markup=self.markup.change_variables_markup())
                case text if text == self.config.admin_home_menu.get('add_admin'):
                    admin.admin_do_input = True
                    admin.admin_input_val = self.config.admin_inner_vars['waiting_new_admin_name']
                    self.database.session.commit()
                    self.bot.send_message(message.chat.id, "Введите имя админа: ",
                                          reply_markup=self.markup.cancel_markup())
                case text if text == self.config.admin_home_menu.get('delete_admin'):
                    admins = self.database.session.query(Admin).all()
                    text = "\n".join([f"{a.name} (ID: {a.id})" for a in admins if
                                      a.id != self.config.super_admin_id and a.id != str(message.from_user.id)])
                    admin.admin_do_input = True
                    admin.admin_input_val = self.config.admin_inner_vars['waiting_deleting_admin_id']
                    self.database.session.commit()
                    self.bot.send_message(message.chat.id,
                                          f"Лист админов:\n{text}\nВведите ID админа которую хотите удалить: ",
                                          reply_markup=self.markup.cancel_markup())
                case text if text == self.config.admin_home_menu.get('add_channel'):
                    admin.admin_do_input = True
                    admin.admin_input_val = self.config.admin_inner_vars['waiting_new_channel_link']
                    self.database.session.commit()
                    self.bot.send_message(message.chat.id,
                                          "Помните, чтобы делать проверку на подписку пользователей, бот должен быть добавлен как администратор канала.\n\nВставьте ссылку на канал: ",
                                          reply_markup=self.markup.cancel_markup())
                case text if text == self.config.admin_home_menu.get('delete_channel'):
                    partners = self.database.session.query(Partner).all()
                    partner_list_text = "\n".join([f"{partner.link} (ID: {partner.id})" for partner in partners])
                    admin.admin_do_input = True
                    admin.admin_input_val = self.config.admin_inner_vars['waiting_deleting_channel_id']
                    self.database.session.commit()
                    self.bot.send_message(message.chat.id,
                                          f"Лист каналов:\n{partner_list_text}\nВведите ID канала которую хотите удалить: ",
                                          reply_markup=self.markup.cancel_markup())
                case text if text == self.config.admin_home_menu.get('view_bot_statistics'):
                    numericVariable = self.get_numeric_variables()
                    self.bot.send_message(message.chat.id,
                                          f"Общее количество пользователей: {numericVariable.total_users_amount}\n\nАктивные: {numericVariable.active_users_amount}\nМертвые: {numericVariable.passive_users_amount}",
                                          reply_markup=self.markup.admin_home_markup())
                case text if text == self.config.admin_home_menu.get('send_message'):
                    admin.admin_do_input = True
                    admin.admin_input_val = self.config.admin_inner_vars['send_button']
                    self.database.session.commit()
                    self.bot.send_message(message.chat.id,
                                          f"Введите сообщение которую хотите отправить пользователям:",
                                          reply_markup=self.markup.cancel_markup())
                case text if text == self.config.admin_home_menu.get('view_channel_statistics'):
                    text = 'Статистика вовлеченных ботом пользователей:'
                    results = self.database.session.query(
                        Subscription.channel_id,
                        func.count(Subscription.user_id).label('num_users')
                    ).group_by(Subscription.channel_id).all()

                    results_dict = {channel_id: num_users for channel_id, num_users in results}
                    partners = self.database.session.query(Partner).all()
                    for p in partners:
                        num = results_dict.get(p.id, 0)
                        text += f'\n\nChannel link: {p.link}\nSubscribed users: {num}'
                    self.bot.send_message(message.chat.id, text, reply_markup=self.markup.admin_home_markup())

        @self.bot.callback_query_handler(func=lambda call: True)
        def handle_callback_query(call):
            user = self.database.session.query(User).get(str(call.from_user.id))

            match call.data:
                case 'view_post':
                    view_post_procedure(user=user, call=call)
                case 'invite_friend':
                    self.bot.edit_message_text(get_invite_text(user=user), parse_mode='HTML', chat_id=call.message.chat.id,
                                               message_id=call.message.message_id)
                case 'join_channel':
                    join_channel_procedure(user=user, call=call)
                case 'withdraw':
                    self.bot.edit_message_text(get_withdraw_text(user=user), parse_mode='HTML', chat_id=call.message.chat.id,
                                          message_id=call.message.message_id)
                case 'checking_user_subscription':
                    checking_user_subscription(user=user, call=call)

        def checking_user_subscription(user, call):
            numeric_variables = self.get_numeric_variables()
            try:
                chat_member = self.bot.get_chat_member(user.current_channel_id, int(user.id))  # Synchronous call
                if chat_member.status in ['member', 'administrator', 'creator']:
                    subscription = Subscription(user_id=user.id, channel_id=user.current_channel_id)
                    self.database.session.add(subscription)
                    user.balance += numeric_variables.join_channel_price
                    self.database.session.commit()
                    if user.language == self.config.language_RU:
                        self.bot.edit_message_text(f'Поздравляем! Вы заработали {numeric_variables.join_channel_price} сом',
                                              chat_id=call.message.chat.id, message_id=call.message.message_id)
                    else:
                        self.bot.edit_message_text(f'Куттуктайбыз! Сиз {numeric_variables.join_channel_price} сом таптыңыз',
                                              chat_id=call.message.chat.id, message_id=call.message.message_id)
                    time.sleep(3)
                    join_channel_procedure(user=user, call=call)
                else:
                    if user.language == self.config.language_RU:
                        self.bot.edit_message_text(f'❌ Вы не являетесь подписчиком данного канала',
                                              chat_id=call.message.chat.id, message_id=call.message.message_id)
                    else:
                        self.bot.edit_message_text(f'❌ Сиз бул каналга жазылуучу эмессиз', chat_id=call.message.chat.id,
                                              message_id=call.message.message_id)
                    time.sleep(3)
                    join_channel_procedure(user=user, call=call)
            except Exception as e:
                print(e)  # For debugging purposes
                self.bot.edit_message_text(f'Произошло ошибка во время проверки',
                                      chat_id=call.message.chat.id, message_id=call.message.message_id)
            user.current_channel_id = '0'
            self.database.session.commit()

        def join_channel_procedure(user, call):
            found = False
            numeric_variable = self.get_numeric_variables()
            sub_id_tuples = self.database.session.query(
                            Subscription.channel_id
                        ).filter(Subscription.user_id == user.id).all()
            sub_ids = [channel_id[0] for channel_id in sub_id_tuples]
            for users_channel_id in sub_ids:
                chat_member = self.bot.get_chat_member(users_channel_id, int(user.id))  # Synchronous call
                if chat_member.status not in ['member', 'administrator', 'creator']:
                    found = True
                    channel = self.database.session.query(Partner).get(users_channel_id)
                    if user.language == self.config.language_RU:
                        self.bot.send_message(call.message.chat.id,
                                         f"Вы отписались от канала\n{channel.link}\n\nC баланса снимается сумма: {numeric_variable.join_channel_price} сом")
                    else:
                        self.bot.send_message(call.message.chat.id,
                                         f"Сиз каналга жазылууну токтоттуңуз\n{channel.link}\n\nСумма баланстан чыгарылат: {numeric_variable.join_channel_price} сом")
                    user.balance -= numeric_variable.join_channel_price
                    subscription = self.database.session.query(Subscription).filter_by(user_id=user.id, channel_id=channel.id).first()
                    self.database.session.delete(subscription)
                    self.database.session.commit()
                    time.sleep(1)

            if found:
                return

            partners = self.database.session.query(Partner).all()
            for partner in partners:
                if partner.id not in sub_ids:
                    if user.language == self.config.language_RU:
                        self.bot.edit_message_text(
                            f'<b>Подпишись на канал</b>\n{partner.link}\n\n<b>и заработай {numeric_variable.join_channel_price} сом</b>',
                            chat_id=call.message.chat.id,
                            message_id=call.message.message_id, parse_mode='HTML',
                            reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                types.InlineKeyboardButton('Проверить подписку',
                                                           callback_data='checking_user_subscription')))
                    else:
                        self.bot.edit_message_text(
                            f'<b>Каналга жазылыңыз</b>\n{partner.link}\n\n<b>жана {numeric_variable.join_channel_price} сом табат</b>',
                            chat_id=call.message.chat.id,
                            message_id=call.message.message_id, parse_mode='HTML',
                            reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                types.InlineKeyboardButton('Жазылууну текшерүү',
                                                           callback_data='checking_user_subscription')))
                    user.current_channel_id = partner.id
                    self.database.session.commit()
                    return

            if user.language == self.config.language_RU:
                self.bot.edit_message_text(
                    f'❌ На данный вы подписались на все каналы\n<i>Вы можете дальше зарабатывать деньги приглашая друзей</i>',
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id, parse_mode='HTML')
            else:
                self.bot.edit_message_text(
                    f'❌ Учурда бардык каналдарга жазылдыңыз\n<i>Досторду чакыруу менен акча табууну уланта аласыз</i>',
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id, parse_mode='HTML')




        def get_invite_text(user):
            numeric_variable = self.get_numeric_variables()
            invited_num = self.database.session.query(
                func.count(User.id)
            ).filter(User.invited_from_id == user.id).scalar()
            text_ru = f"🗣Пригласи своих друзей и получи за это деньги\n\nОтправь друзьям данную ссылку:\n{self.config.bot_partner_link + user.id}\n<b>{numeric_variable.invite_friend_price} сом за каждого приглашенного друга</b>\n<i>Чтобы деньги зачислились, приглашенные друзья должны запустить бот</i>\n\n▪️<b>Количество приглашенных друзей</b>: {invited_num}\n▪️<b>Заработано денег</b>: {invited_num * numeric_variable.invite_friend_price}"
            text_kg = f"🗣Досторуңузду чакырыңыз жана ал үчүн акча алыңыз\n\nБул шилтемени досторуңузга жөнөтүңүз:\n{self.config.bot_partner_link + user.id}\n<b>Ар бир чакырылган дос үчүн {numeric_variable.invite_friend_price} сомдон</b>\n<i>Акча чегерилиши үчүн, чакырылган достор ботту иштетиши керек</i>\n\n▪️<b>Чакырылган достордун саны</b>: {invited_num}\n▪️<b>Табылган акча</b>: {invited_num * numeric_variable.invite_friend_price}"
            return text_ru if user.language == self.config.language_RU else text_kg

        def get_withdraw_text(user):
            numeric_variable = self.get_numeric_variables()
            invited_num = self.database.session.query(
                func.count(User.id)
            ).filter(User.invited_from_id == user.id).scalar()
            text_ru = f"❌\n<b>Минимальная сумма для снятие денег</b>: {numeric_variable.min_withdrawal_amount} сом\n<b>Минимальное количество приглашенных друзей</b>: {numeric_variable.min_invited_friends}\n\n<i>Ваш баланс</i>: {user.balance} сом\n<i>Количество приглашенных друзей</i>: {invited_num}"
            text_kg = f"❌\n<b>Акча алуу үчүн минималдуу сумма</b>: {numeric_variable.min_withdrawal_amount} сом\n<b>Чакырылган достордун минималдуу саны</b>: {numeric_variable.min_invited_friends}\n\n<i>Сиздин балансыңыз</i>: {user.balance} сом\n<i>Чакырылган достордун саны</i>: {invited_num}"
            return text_ru if user.language == self.config.language_RU else text_kg

        def view_post_procedure(user, call):
            numeric_variable = self.get_numeric_variables()
            if user.view_post_time > datetime.datetime.now():
                time_difference = user.view_post_time - datetime.datetime.now()
                seconds = time_difference.seconds
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                seconds = (seconds % 3600) % 60
                if user.language == self.config.language_RU:
                    self.bot.edit_message_text(
                        f'Просмотр поста доступно через:\n{hours} часов, {minutes} минут, {seconds} секунд',
                        chat_id=call.message.chat.id, message_id=call.message.message_id)
                else:
                    self.bot.edit_message_text(
                        f'Постту көрүү:\n{hours} саат, {minutes} мүнөт, {seconds} секунд убакыттан кийин',
                        chat_id=call.message.chat.id, message_id=call.message.message_id)
                return

            partners = self.database.session.query(Partner).all()
            for i in range(len(partners)):
                if user.language == self.config.language_RU:
                    self.bot.edit_message_text(f'<b>Просмотр поста</b>\nID: {partners[i].id}\n\n{i+1}/{len(partners)}', chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='HTML')
                else:
                    self.bot.edit_message_text(f'<b>Постту көрүү</b>\nID: {partners[i].id}\n\n{i+1}/{len(partners)}', chat_id=call.message.chat.id,
                                          message_id=call.message.message_id, parse_mode='HTML')
                time.sleep(0.3)
            if user.language == self.config.language_RU:
                self.bot.edit_message_text(f'Просмотр постов выполнено\n<b>Вы заработали {numeric_variable.view_post_price} сом</b>', chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='HTML')
            else:
                self.bot.edit_message_text(f'Постторду көрүү аяктады\n<b>Сиз {numeric_variable.view_post_price} сом таптыңыз</b>', chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='HTML')
            user.balance += numeric_variable.view_post_price
            user.view_post_time = datetime.datetime.now()+datetime.timedelta(hours=12)
            self.database.session.commit()

