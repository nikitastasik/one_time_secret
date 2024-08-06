import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()

db_user = os.getenv("DATABASE_USER")
db_password = os.getenv("DATABASE_PASSWORD")
db_host = os.getenv("DATABASE_HOST")
db_port = os.getenv("DATABASE_PORT")
db_name = os.getenv("DATABASE_NAME")

# Формирование строки подключения
DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
print(DATABASE_URL)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def init_db():
    """
    Инициализация базы данных: создание всех таблиц, если их нет.
    """
    Base.metadata.create_all(bind=engine)


# Вызов инициализации базы данных при запуске модуля
if __name__ == "__main__":
    init_db()
