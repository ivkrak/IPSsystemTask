#!/root/IPSsystemTask/venv/bin/python3
import uuid

import payment
import billmgr.db
import billmgr.exception

import billmgr.logger as logging

import xml.etree.ElementTree as ET

MODULE = 'payment'
logging.init_logging('pmtestpayment')
logger = logging.get_logger('pmtestpayment')


class TestPaymentModule(payment.PaymentModule):
    def __init__(self):
        super().__init__()

        self.features[payment.FEATURE_CHECKPAY] = True
        self.features[payment.FEATURE_REDIRECT] = True
        self.features[payment.FEATURE_NOT_PROFILE] = True
        self.features[payment.FEATURE_PMVALIDATE] = True

        self.params[payment.PAYMENT_PARAM_PAYMENT_SCRIPT] = "/mancgi/testpayment"

    # в тестовом примере валидация проходит успешно, если
    # Идентификатор терминала = rick, пароль терминала = morty
    def PM_Validate(self, xml: ET.ElementTree):
        logger.warning('''
        .
⠄⠄⠄⠄⠄⠄⣀⣤⣶⣾⣿⣿⣿⣿⣷⣶⣤⣄⡀⠄⠄⠄⠄⠄
⠄⠄⠄⢀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣄⠄⠄⠄
⠄⠄⣰⣿⣿⣿⣿⣿⠿⠛⠋⠉⠉⠙⠛⠻⣿⣿⣿⣿⣿⣧⠄⠄
⠄⢰⣿⣿⣿⡿⠋⠁⠄⠄⠄⠄⠄⠄⠄⢀⣀⠙⠻⣿⣿⣿⣧⠄
⠄⣼⣿⣿⡿⠖⣫⡥⢤⣀⠄⠄⠄⠄⢀⣤⠭⣍⣓⠘⢿⣿⣿⡆
⣼⣿⣿⡟⢠⠏⠄⠄⠄⠈⠹⡄⠄⡼⠁⠄⠄⠄⠈⢧⠘⣿⣿⣷
⣿⣿⣿⠁⣾⠄⠄⠶⠄⠄⠄⡇⢸⡇⠄⠄⠛⠄⠄⢸⠄⢹⣿⣿
⠸⣿⣿⠄⠸⣄⠄⠄⠄⠄⣰⠃⢀⠳⣀⠄⠄⠄⢀⠏⠄⢸⣿⡇
⢰⡟⢹⡀⠄⠈⠙⠒⠒⠋⠁⢲⣸⠇⠈⠙⠒⠋⠁⠄⠄⣸⠙⣷
⠸⣧⡀⢧⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⢠⣇⣠⡿
⠄⠈⠛⠛⣧⠄⠄⠄⠄⠤⠴⠖⠒⠲⠦⠄⠄⠄⠄⢠⡾⠉⠉⠄
⠄⠄⠄⠄⠈⠷⣤⡀⠄⠄⠄⠄⠄⠄⠄⠄⠄⣠⡴⠟⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠈⠛⠳⢶⣤⣤⣤⣤⣴⠶⠛⠉⠄⠄⠄⠄⠄⠄


        ''')
        logger.warning("run pmvalidate")
        logger.warning(f'DEBUG | {xml}=')
        # мы всегда можем вывести xml в лог, чтобы изучить, что приходит :)
        logger.warning(f"xml input: {ET.tostring(xml.getroot(), encoding='unicode')}")

        yookassa_shop_id_node = xml.find('./yookassa_shop_id')
        yookassa_secret_node = xml.find('./yookassa_secret')
        yookassa_shop_id = yookassa_shop_id_node.text if yookassa_shop_id_node is not None else ''
        yookassa_secret = yookassa_secret_node.text if yookassa_secret_node is not None else ''

        if not (yookassa_shop_id or yookassa_secret):
            raise billmgr.exception.XmlException('wrong_terminal_info')
        auth = (yookassa_shop_id, yookassa_secret)
        logger.warning(f'{auth=}')
        # try:
        #     url = "https://api.yookassa.ru/v3/payments"
        #
        #     # Аутентификация
        #     auth = (yookassa_shop_id, yookassa_secret)
        #
        #     # Заголовки
        #     headers = {
        #         'Idempotence-Key': uuid.uuid4(),
        #         'Content-Type': 'application/json',
        #     }
        #     data = {
        #         "amount": {
        #             "value": metadata['amount'],
        #             "currency": "RUB"
        #         },
        #         "confirmation": {
        #             "type": "redirect",
        #             "return_url": return_url,
        #         },
        #         "capture": True,
        #         "description": description,
        #         "metadata": metadata
        #     }
        #
        #     response = requests.post(url, json=data, headers=headers, auth=auth)
        # except:
        #     ...

    # в тестовом примере получаем необходимые платежи
    # и переводим их все в статус 'оплачен'
    def CheckPay(self):
        logger.info("run checkpay")

        # получаем список платежей в статусе оплачивается
        # и которые используют обработчик pmtestpayment
        payments = billmgr.db.db_query(f'''
            SELECT p.id FROM payment p
            JOIN paymethod pm
            WHERE module = 'pmtestpayment' AND p.status = {payment.PaymentStatus.INPAY.value}
        ''')

        for p in payments:
            logger.info(f"change status for payment {p['id']}")
            payment.set_paid(p['id'], '', f"external_{p['id']}")


TestPaymentModule().Process()
