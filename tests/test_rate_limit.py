from app.main import app, get_remote_address
from slowapi import Limiter

COUNT_LIMIT = 10


def test_rate_limit(client):
    # Создаем новый лимитер с лимитом 10 запросов в минуту
    new_limiter = Limiter(key_func=get_remote_address, default_limits=["10/minute"])
    app.state.limiter = new_limiter

    # Обновляем middleware, чтобы использовать новый лимитер
    app.middleware_stack = app.build_middleware_stack()

    # Делаем 10 запросов до достижения лимита
    for _ in range(COUNT_LIMIT):
        response = client.post("/generate", json={"secret": "My very secret message", "passphrase": "my_passphrase"})
        assert response.status_code == 200

    # Следующий запрос должен вызвать превышение лимита
    response = client.post("/generate", json={"secret": "My very secret message", "passphrase": "my_passphrase"})
    assert response.status_code == 429
    assert response.json() == {"detail": "Too Many Requests"}
