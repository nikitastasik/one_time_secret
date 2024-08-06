from pydantic import BaseModel


class SecretCreate(BaseModel):
    secret: str
    passphrase: str


class SecretResponse(BaseModel):
    secret_key: str


class Passphrase(BaseModel):
    passphrase: str
