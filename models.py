from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base, Session
import uuid
from cryptography.fernet import Fernet
from typing import Optional

Base = declarative_base()


class Secret(Base):
    """
    Модель данных для хранения секретов в базе данных.

    Атрибуты:
        id (int): Уникальный идентификатор секрета.
        secret_key (str): Уникальный ключ, используемый для доступа к секрету.
        encrypted_secret (str): Зашифрованный секрет.
        encrypted_passphrase (str): Зашифрованная кодовая фраза.
    """

    __tablename__ = "secrets"

    id = Column(Integer, primary_key=True, index=True)
    secret_key = Column(String, unique=True, index=True)
    encrypted_secret = Column(String)
    encrypted_passphrase = Column(String)

    @staticmethod
    def create_secret(db: Session, secret: str, passphrase: str, encryption_key: bytes) -> str:
        """
        Генерирует уникальный ключ для одноразового секрета.

        :param db: Сессия базы данных.
        :param secret: Секрет, который нужно зашифровать и сохранить.
        :param passphrase: Кодовая фраза для доступа к секрету.
        :param encryption_key: Ключ шифрования для Fernet.
        :return: Словарь с ключом секрета.
        """
        fernet = Fernet(encryption_key)
        secret_key = str(uuid.uuid4())
        encrypted_secret = fernet.encrypt(secret.encode())
        encrypted_passphrase = fernet.encrypt(passphrase.encode())

        db_secret = Secret(
            secret_key=secret_key,
            encrypted_secret=encrypted_secret.decode(),
            encrypted_passphrase=encrypted_passphrase.decode()
        )
        db.add(db_secret)
        db.commit()
        db.refresh(db_secret)
        return secret_key

    @staticmethod
    def get_secret(db: Session, secret_key: str, passphrase: str, encryption_key: bytes) -> Optional[str]:
        """
        Возвращает секрет по переданному ключу и кодовой фразе.

        :param db: Сессия базы данных.
        :param secret_key: Уникальный ключ секрета.
        :param passphrase: Кодовая фраза для расшифровки секрета.
        :param encryption_key: Ключ шифрования для Fernet.
        :return: Расшифрованный секрет, если ключ и кодовая фраза верны, иначе None.
        """
        fernet = Fernet(encryption_key)
        secret = db.query(Secret).filter(Secret.secret_key == secret_key).first()
        if secret is None:
            return None

        decrypted_passphrase = fernet.decrypt(secret.encrypted_passphrase.encode()).decode()
        if decrypted_passphrase != passphrase:
            return None

        decrypted_secret = fernet.decrypt(secret.encrypted_secret.encode()).decode()
        db.delete(secret)
        db.commit()
        return decrypted_secret
