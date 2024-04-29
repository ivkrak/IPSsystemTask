import uuid
import requests

yookassa_API_url = 'https://api.yookassa.ru/v3'


def create(metadata: dict):
    url = f'{yookassa_API_url}/payments'
    auth = requests.auth.HTTPBasicAuth(settings.YOO_KASSA_ACCOUNT_ID, settings.YOO_KASSA_SECRET_KEY)
    headers = {
        'Idempotence-Key': str(uuid.uuid4()),
        'Content-Type': 'application/json'
    }
    data = {
        "amount": {
            "value": metadata['amount'],
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": settings.MARKET_URL
        },
        "capture": True,
        "description": "Оплата неведомой хуйни",
        "metadata": metadata
    }

    response = requests.post(url, json=data, headers=headers, auth=auth)

    if response.status_code == 200:
        payment_dict = response.json()
        return payment_dict['confirmation']['confirmation_url'], payment_dict['id']
    else:
        response.raise_for_status()
        raise requests.exceptions.RequestException(response.text)


def check(payment_id, user_id: int | str, username: str):
    url = f"{yookassa_API_url}/payments/{payment_id}"
    auth = requests.auth.HTTPBasicAuth(settings.YOO_KASSA_ACCOUNT_ID, settings.YOO_KASSA_SECRET_KEY)

    response = requests.get(url, auth=auth)
    payment = response.json()

    if payment['status'] == 'succeeded':
        metadata = payment['metadata']
        return True
    else:
        return False