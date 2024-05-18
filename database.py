from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from argon2 import PasswordHasher
import random

Base = declarative_base()
ph = PasswordHasher()

class User(Base):
    __tablename__ = 'users'
    username = Column(String, primary_key=True)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    salt = Column(String, nullable=False)

class InventoryItem(Base):
    __tablename__ = 'inventory'
    item_name = Column(String, primary_key=True)
    quantity = Column(Integer, nullable=False)
    barcode = Column(String, nullable=False, unique=True)

class DatabaseManager:
    def __init__(self, db_file):
        self.engine = create_engine(f'sqlite:///{db_file}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def add_user(self, username, password, role):
        session = self.Session()
        salt = os.urandom(32).hex()
        hashed_password = ph.hash(password + salt)
        user = User(username=username, password=hashed_password, role=role, salt=salt)
        try:
            session.add(user)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(e)
            return False
        finally:
            session.close()

    def verify_user(self, username, password):
        session = self.Session()
        try:
            user = session.query(User).filter_by(username=username).one()
            if ph.verify(user.password, password + user.salt):
                return user.role
        except Exception as e:
            print(e)
            return None
        finally:
            session.close()

    def add_inventory_item(self, item_name, quantity, barcode):
        session = self.Session()
        item = InventoryItem(item_name=item_name, quantity=quantity, barcode=barcode)
        try:
            session.add(item)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(e)
            return False
        finally:
            session.close()

    def update_inventory_item(self, item_name, quantity):
        session = self.Session()
        try:
            item = session.query(InventoryItem).filter_by(item_name=item_name).one()
            item.quantity += quantity
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(e)
            return False
        finally:
            session.close()

    def get_inventory(self):
        session = self.Session()
        try:
            return session.query(InventoryItem).all()
        finally:
            session.close()

    def delete_user(self, username):
        session = self.Session()
        try:
            user = session.query(User).filter_by(username=username).one()
            session.delete(user)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(e)
            return False
        finally:
            session.close()

def generate_ean13():
    base_number = ''.join([str(random.randint(0, 9)) for _ in range(12)])
    checksum = calculate_ean13_checksum(base_number)
    return base_number + checksum

def calculate_ean13_checksum(base_number):
    odd_sum = sum(int(base_number[i]) for i in range(0, 12, 2))
    even_sum = sum(int(base_number[i]) for i in range(1, 12, 2))
    total_sum = odd_sum + even_sum * 3
    return str((10 - (total_sum % 10)) % 10)
