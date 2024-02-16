from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import Config
from model import Base, NumericVariable, Admin


class Database:
    def __init__(self, config: Config, database_user: str, database_password: str, database_host: str, database_port: int, database_name: str):
        engine = create_engine(
            f'postgresql+psycopg2://{database_user}:{database_password}@{database_host}:{database_port}/{database_name}')
        s = sessionmaker(bind=engine)
        self.session = s()
        self.config = config
        Base.metadata.create_all(engine)
        self.initialize_numeric_variables()

    def initialize_numeric_variables(self):
        # Check if a record with ID = 1 exists
        existing_num_values = self.session.query(NumericVariable).filter_by(id=1).first()
        existing_admin = self.session.query(Admin).filter_by(id=self.config.super_admin_id).first()
        # If not, create and add the new record
        if not existing_admin:
            default_values = Admin(
                id=self.config.super_admin_id,
                name=self.config.super_admin_name
            )
            self.session.add(default_values)
            self.session.commit()

        if not existing_num_values:
            default_values = NumericVariable(
                invite_friend_price=175,
                join_channel_price=200,
                view_post_price=105,
                min_withdrawal_amount=9000,
                min_invited_friends=5
            )
            self.session.add(default_values)
            self.session.commit()