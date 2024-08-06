# One Time Secret API

Этот проект представляет собой простой API-сервис для генерации и получения одноразовых секретов с использованием FastAPI.

## Возможности

- Генерация одноразового секрета с кодовой фразой.
- Получение одноразового секрета при правильной кодовой фразе.
- Ограничение количества запросов для защиты от злоупотреблений.
- Шифрованное хранение секретов и кодовых фраз.

## Используемые технологии

- Python 3.7
- FastAPI
- PostgreSQL
- Docker & Docker Compose
- SQLAlchemy
- SlowAPI (для ограничения количества запросов)
- Alembic (для миграций базы данных)

## Предварительные требования

Перед началом убедитесь, что у вас установлены следующие компоненты:

- Установлен Python 3.7 (для запуска без Docker).
- Установлен и запущен PostgreSQL (для запуска без Docker).
- Установлены Docker и Docker Compose (для запуска с Docker).
- Аккаунт на GitHub (для клонирования репозитория).

## Установка

## 1. Клонирование репозитория

```bash
git clone https://github.com/your-username/one-time-secret.git
cd one-time-secret
```

## 2. Запуск проекта без Docker

### Создайте виртуальное окружение:

```bash
python3 -m venv venv
source venv/bin/activate  # Для Windows используйте `venv\Scripts\activate`
```

### Установите зависимости:

```bash
pip install -r requirements.txt
```

### Создайте файл .env:

В корневой директории проекта создайте файл `.env` со следующим содержимым:

```
DATABASE_USER=your_user
DATABASE_PASSWORD=your_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=your_database_name
RATE_LIMIT=600
```

### Настройте базу данных:

Убедитесь, что PostgreSQL запущен.

Создайте новую базу данных:

```sql
CREATE DATABASE your_database_name;
```

Примените миграции (если они есть) или позвольте приложению создать необходимые таблицы.

### Запустите приложение:

```bash
uvicorn main:app --reload
```

API будет доступен по адресу `http://127.0.0.1:8000`.

## 3. Запуск проекта с Docker

### Создайте файл .env:

В корневой директории проекта создайте файл `.env` со следующим содержимым:

```
DATABASE_USER=your_user
DATABASE_PASSWORD=your_password
DATABASE_HOST=db
DATABASE_PORT=5432
DATABASE_NAME=your_database_name
RATE_LIMIT=600
```

### Соберите и запустите контейнеры:

```bash
docker-compose up --build
```

Docker скачает необходимые образы, соберет образ приложения и запустит контейнеры. API будет доступен по адресу `http://localhost:8000`.

### Остановка контейнеров:

Чтобы остановить контейнеры, используйте команду:

```bash
docker-compose down
```

## Использование

### Генерация секрета:

Отправьте POST-запрос на `/generate` с следующим JSON-payload:

```json
{
  "secret": "Your secret message",
  "passphrase": "Your passphrase"
}
```

### Получение секрета:

Отправьте POST-запрос на `/secrets/{secret_key}` с следующим JSON-payload:

```json
{
  "passphrase": "Your passphrase"
}
```

Если кодовая фраза верна, вы получите секретное сообщение.

## Тестирование

Чтобы запустить тесты, убедитесь, что все зависимости установлены, и выполните команду:

```bash
pytest --cov=.
```

Если вы используете Docker, вы можете запустить тесты внутри контейнера:

```bash
docker-compose exec web pytest --cov=.
```
