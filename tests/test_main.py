def test_create_secret(client):
    response = client.post("/generate", json={"secret": "My very secret message", "passphrase": "my_passphrase"})
    assert response.status_code == 200
    assert "secret_key" in response.json()


def test_get_secret(client):
    # Сначала создаем секрет
    create_response = client.post("/generate", json={"secret": "My very secret message", "passphrase": "my_passphrase"})
    secret_key = create_response.json()["secret_key"]

    # Теперь пытаемся получить секрет
    get_response = client.post(f"/secrets/{secret_key}", json={"passphrase": "my_passphrase"})
    assert get_response.status_code == 200
    assert get_response.json()["secret"] == "My very secret message"


def test_get_secret_with_invalid_passphrase(client):
    # Сначала создаем секрет
    create_response = client.post("/generate", json={"secret": "My very secret message", "passphrase": "my_passphrase"})
    secret_key = create_response.json()["secret_key"]

    # Пытаемся получить секрет с неверной кодовой фразой
    get_response = client.post(f"/secrets/{secret_key}", json={"passphrase": "wrong_passphrase"})
    assert get_response.status_code == 404


def test_secret_deletion_after_retrieval(client):
    # Сначала создаем секрет
    create_response = client.post("/generate", json={"secret": "My very secret message", "passphrase": "my_passphrase"})
    secret_key = create_response.json()["secret_key"]

    # Получаем секрет один раз
    client.post(f"/secrets/{secret_key}", json={"passphrase": "my_passphrase"})

    # Пытаемся получить секрет снова
    get_response = client.post(f"/secrets/{secret_key}", json={"passphrase": "my_passphrase"})
    assert get_response.status_code == 404


def test_get_secret_with_invalid_key(client):
    # Пытаемся получить секрет с неверным ключом
    get_response = client.post("/secrets/invalid_key", json={"passphrase": "my_passphrase"})
    assert get_response.status_code == 404


def test_create_secret_with_missing_fields(client):
    # Пытаемся создать секрет с отсутствующим полем 'passphrase'
    response = client.post("/generate", json={"secret": "My very secret message"})
    assert response.status_code == 422
    assert "detail" in response.json()

    # Пытаемся создать секрет с отсутствующим полем 'secret'
    response = client.post("/generate", json={"passphrase": "my_passphrase"})
    assert response.status_code == 422
    assert "detail" in response.json()


def test_get_secret_with_missing_passphrase(client):
    # Сначала создаем секрет
    create_response = client.post("/generate", json={"secret": "My very secret message", "passphrase": "my_passphrase"})
    secret_key = create_response.json()["secret_key"]

    # Пытаемся получить секрет без кодовой фразы
    get_response = client.post(f"/secrets/{secret_key}", json={})
    assert get_response.status_code == 422
    assert "detail" in get_response.json()
