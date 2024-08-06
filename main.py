from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
import models
import schemas
import database
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.responses import JSONResponse
from dotenv import load_dotenv
import os

# Загрузка переменных окружения
load_dotenv()

# Получаем значение лимита запросов из переменной окружения
RATE_LIMIT = os.getenv("RATE_LIMIT", "600")

# Создаем экземпляр приложения FastAPI
app = FastAPI(
    title="One-Time Secret API",
    description="API для создания и получения одноразовых секретов. "
                "Это API позволяет создавать одноразовые секреты, защищенные кодовой фразой, "
                "и получать их по уникальному ключу. Секреты удаляются после первого доступа.",
    version="1.0.0",
)

# Настройка лимитера с использованием значения из переменной окружения
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Добавление обработчика исключений для превышения лимита запросов
app.add_exception_handler(RateLimitExceeded, lambda request, exc: JSONResponse(
    status_code=429,
    content={"detail": "Too Many Requests"},
))

# Добавление middleware для применения лимитов
app.add_middleware(SlowAPIMiddleware)

# Инициализация базы данных
models.Base.metadata.create_all(bind=database.engine)


@app.post(
    "/generate",
    response_model=schemas.SecretResponse,
    summary="Создание секрета",
    description="Генерирует уникальный ключ для одноразового секрета, который можно получить только один раз. "
                "Секрет зашифрован и доступен только по кодовой фразе.",
    response_description="Возвращает уникальный ключ для доступа к секрету.",
    tags=["Секреты"],
)
@limiter.limit(f"{RATE_LIMIT}/minute")
async def generate_secret(
    request: Request,
    secret_create: schemas.SecretCreate,
    db_session: Session = Depends(database.get_db)
) -> dict:
    """
    Генерирует уникальный ключ для одноразового секрета.

    :param request: HTTP запрос. Нужен для корректной работы slowapi.
    :param secret_create: Модель данных с секретом и кодовой фразой.
    :param db_session: Сессия базы данных.
    :return: Словарь с ключом секрета.
    """
    secret_key = models.Secret.create_secret(
        db_session=db_session,
        secret=secret_create.secret,
        passphrase=secret_create.passphrase
    )
    return {"secret_key": secret_key}


@app.post(
    "/secrets/{secret_key}",
    summary="Получение секрета",
    description="Возвращает секрет по переданному ключу и кодовой фразе. "
                "Секрет может быть получен только один раз, после чего он будет удален.",
    response_description="Возвращает расшифрованный секрет, если ключ и кодовая фраза верны.",
    tags=["Секреты"],
)
@limiter.limit(f"{RATE_LIMIT}/minute")
async def get_secret(
    request: Request,
    secret_key: str,
    passphrase: schemas.Passphrase,
    db_session: Session = Depends(database.get_db)
) -> dict:
    """
    Возвращает секрет по переданному ключу и кодовой фразе.

    :param request: HTTP запрос. Нужен для корректной работы slowapi.
    :param secret_key: Уникальный ключ секрета.
    :param passphrase: Кодовая фраза для доступа к секрету.
    :param db_session: Сессия базы данных.
    :return: Словарь с расшифрованным секретом или сообщение об ошибке.
    """
    secret = models.Secret.get_secret(
        db_session=db_session,
        secret_key=secret_key,
        passphrase=passphrase.passphrase
    )
    if secret is None:
        raise HTTPException(status_code=404, detail="Secret not found or invalid passphrase")

    return {"secret": secret}

# Обработчики исключений

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Обработчик для всех исключений HTTPException, возвращает JSON ответ с кодом ошибки и сообщением.
    """
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Обработчик для исключений RequestValidationError, возникающих при валидации входящих данных.
    Возвращает JSON ответ с кодом ошибки 422 и сообщением об ошибках валидации.
    """
    return JSONResponse(status_code=422, content={"detail": exc.errors()})
