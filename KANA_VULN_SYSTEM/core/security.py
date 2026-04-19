from __future__ import annotations

import os

from cryptography.fernet import Fernet, InvalidToken


class SecretManager:
    def __init__(self, master_key: str | None) -> None:
        self._fernet: Fernet | None = None
        if master_key:
            self._fernet = Fernet(master_key.encode('utf-8'))

    @classmethod
    def from_environment(cls) -> 'SecretManager':
        return cls(os.getenv('KANA_MASTER_KEY'))

    @staticmethod
    def generate_master_key() -> str:
        return Fernet.generate_key().decode('utf-8')

    def encrypt(self, plaintext: str) -> str:
        if self._fernet is None:
            raise RuntimeError('KANA_MASTER_KEY is not configured; cannot encrypt secret.')
        token = self._fernet.encrypt(plaintext.encode('utf-8')).decode('utf-8')
        return f'enc:{token}'

    def decrypt(self, ciphertext: str) -> str:
        if self._fernet is None:
            raise RuntimeError('KANA_MASTER_KEY is not configured; cannot decrypt secret.')
        token = ciphertext.removeprefix('enc:')
        try:
            value = self._fernet.decrypt(token.encode('utf-8'))
        except InvalidToken as exc:
            raise RuntimeError('Unable to decrypt secret. Check KANA_MASTER_KEY.') from exc
        return value.decode('utf-8')

    def read_secret(self, env_name: str) -> str:
        encrypted_key = f'{env_name}_ENC'
        encrypted_value = os.getenv(encrypted_key)
        if encrypted_value:
            return self.decrypt(encrypted_value)

        plaintext = os.getenv(env_name)
        if plaintext:
            if plaintext.startswith('enc:'):
                return self.decrypt(plaintext)
            return plaintext

        return ''


def mask_secret(secret: str, keep: int = 4) -> str:
    if not secret:
        return ''
    if len(secret) <= keep:
        return '*' * len(secret)
    return f"{'*' * (len(secret) - keep)}{secret[-keep:]}"
