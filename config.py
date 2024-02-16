class Config:
    def __init__(self, super_admin_id: str, super_admin_name: str, bot_id: str, bot_partner_link: str):
        self.super_admin_id = super_admin_id
        self.super_admin_name = super_admin_name
        self.bot_id = bot_id
        self.bot_partner_link = bot_partner_link

        self.language_RU = 'RU'
        self.language_KG = 'KG'

        self.user_home_menu = {
            self.language_RU: {
                'language': '🇰🇬 На киргизском',
                'balance': '💰 Баланс',
                'partners': '🤝 Позвать друга',
                'earn_money': '💸 Заработать',
            },
            self.language_KG: {
                'language': '🇷🇺 Орусча',
                'balance': '💰 Баланс',
                'partners': '🤝 Дос чакыруу',
                'earn_money': '💸 Акча табуу',
            }
        }

        self.user_earn_money_menu = {
            self.language_RU: {
                'invite_friend': '🗣 Позвать друга',
                'join_channel': '📌 Присоединиться к каналу',
                'view_post': '👁 Посмотреть пост',
            },
            self.language_KG: {
                'invite_friend': '🗣 Дос чакыруу',
                'join_channel': '📌 Каналга кошулуу',
                'view_post': '👁 Постту көрүү',
            }
        }

        self.admin_home_menu = {
            'add_admin': 'Добавить админа',
            'delete_admin': 'Удалить админа',
            'add_channel': 'Добавить канал',
            'delete_channel': 'Удалить канал',
            'view_channel_statistics': 'Посмотреть статистику каналов',
            'view_bot_statistics': 'Посмотреть статистику бота',
            'change_variable': 'Поменять значения',
            'send_message': 'Отправить сообщение пользователям'
        }

        self.admin_inner_vars = {
            'cancel': 'Отменить',
            'send_button': 'Отправить',
            'waiting_deleting_admin_id': 'Ожидание ID удаляемого админа',
            'waiting_new_admin_name': 'Ожидание имени нового админа',
            'waiting_new_admin_id': 'Ожидание ID нового админа',
            'waiting_new_channel_link': 'Ожидание ссылки нового канала',
            'waiting_new_channel_id': 'Ожидание ID нового канала',
            'waiting_deleting_channel_id': 'Ожидание ID удаляемого канала',
        }
        self.admin_change_variable = {
            'invite_friend': 'Приглашение друга',
            'join_channel': 'Вступление в канал',
            'view_post': 'Просмотр поста',
            'min_withdrawal_amount': 'Минимальный сом для снятие денег',
            'min_invited_friends': 'Минимальное приглашение для снятие денег',
        }


