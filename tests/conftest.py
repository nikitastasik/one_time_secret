import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from database import get_db
from main import app
from fastapi.testclient import TestClient

# Используем SQLite в файле для тестирования
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Фикстура для очистки базы данных перед каждым тестом."""
    # Очищаем базу данных
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db_session = TestingSessionLocal()
    yield db_session
    db_session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Фикстура для переопределения зависимостей FastAPI и использования тестового клиента."""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


# Хук для выполнения после завершения всех тестов
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    yield
    # Проверяем, существует ли файл .coverage
    coverage_file = ".coverage"
    if os.path.exists(coverage_file):
        os.remove(coverage_file)
        terminalreporter.write(f"\nФайл {coverage_file} был удален после тестов.\n")

    # Удаление файла test.db
    test_db_file = "test.db"
    if os.path.exists(test_db_file):
        os.remove(test_db_file)
        terminalreporter.write(f"\nФайл {test_db_file} был удален после тестов.\n")
