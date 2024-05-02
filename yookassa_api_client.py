import uuid
import requests

yookassa_API_url = 'https://api.yookassa.ru/v3'


def create(
        store_id: int | str,
        secret_key: str,
        return_url: str,
        description: str,
        metadata: dict
):
    url = "https://api.yookassa.ru/v3/payments"

    # Аутентификация
    auth = (str(store_id), secret_key)

    # Заголовки
    headers = {
        'Idempotence-Key': uuid.uuid4(),
        'Content-Type': 'application/json',
    }
    data = {
        "amount": {
            "value": metadata['amount'],
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": return_url,
        },
        "capture": True,
        "description": description,
        "metadata": metadata
    }

    response = requests.post(url, json=data, headers=headers, auth=auth)

    if response.status_code == 200:
        return response.json()


def check(store_id: int | str, secret_key: str, payment_id: str):
    url = f"{yookassa_API_url}/payments/{payment_id}"
    auth = (store_id, secret_key)

    response = requests.get(url, auth=auth)
    payment = response.json()

    if payment['status'] == 'succeeded':
        return payment['metadata']
