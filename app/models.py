from sqlalchemy import String, Identity
from sqlalchemy.orm import declarative_base, Session, Mapped, mapped_column
import uuid
import base64
import hashlib
from cryptography.fernet import Fernet, InvalidToken
from typing import Optional

Base = declarative_base()


class Secret(Base):
    __tablename__ = "secrets"

    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True, index=True)
    secret_key: Mapped[str] = mapped_column(String, unique=True, index=True)
    encrypted_secret: Mapped[str] = mapped_column(String)
    encrypted_passphrase: Mapped[str] = mapped_column(String)

    @staticmethod
    def create_secret(db_session: Session, secret: str, passphrase: str) -> str:
        """
        Генерирует уникальный ключ для одноразового секрета.

        :param db_session: Сессия базы данных.
        :param secret: Секрет, который нужно зашифровать и сохранить.
        :param passphrase: Кодовая фраза для доступа к секрету.
        :return: Уникальный ключ секрета.
        """
        # Генерируем ключ шифрования на основе кодовой фразы
        key = base64.urlsafe_b64encode(hashlib.sha256(passphrase.encode()).digest())
        fernet = Fernet(key)

        secret_key = str(uuid.uuid4())
        encrypted_secret = fernet.encrypt(secret.encode()).decode()
        encrypted_passphrase = fernet.encrypt(passphrase.encode()).decode()

        db_secret = Secret(
            secret_key=secret_key,
            encrypted_secret=encrypted_secret,
            encrypted_passphrase=encrypted_passphrase
        )
        db_session.add(db_secret)
        db_session.commit()
        db_session.refresh(db_secret)
        return secret_key

    @staticmethod
    def get_secret(db_session: Session, secret_key: str, passphrase: str) -> Optional[str]:
        """
        Возвращает секрет по переданному ключу и кодовой фразе.

        :param db_session: Сессия базы данных.
        :param secret_key: Уникальный ключ секрета.
        :param passphrase: Кодовая фраза для расшифровки секрета.
        :return: Расшифрованный секрет, если ключ и кодовая фраза верны, иначе None.
        """
        # Генерируем ключ шифрования на основе кодовой фразы
        key = base64.urlsafe_b64encode(hashlib.sha256(passphrase.encode()).digest())
        fernet = Fernet(key)

        secret = db_session.query(Secret).filter(Secret.secret_key == secret_key).first()
        if secret is None:
            return None

        try:
            decrypted_passphrase = fernet.decrypt(secret.encrypted_passphrase.encode()).decode()
        except InvalidToken:
            return None

        if decrypted_passphrase != passphrase:
            return None

        decrypted_secret = fernet.decrypt(secret.encrypted_secret.encode()).decode()
        db_session.delete(secret)
        db_session.commit()
        return decrypted_secret
