#!/root/IPSsystemTask/venv/bin/python3
import sys
import uuid

import requests

# import uuid
import billmgr.logger as logging
import payment

MODULE = 'payment'
logging.init_logging('testpayment')
logger = logging.get_logger('testpayment')


class TestPaymentCgi(payment.PaymentCgi):
    def Process(self):
        store_id: str = ''
        secret_key: str = ''
        return_url: str = ''
        metadata = {'amount': 666}
        description: str = ''
        logger.error(f'TEST_PAYMENT | {self.payment_params=}')
        logger.error(f'TEST_PAYMENT | {self.paymethod_params=}')
        logger.error(f'TEST_PAYMENT | {self.user_params=}')
        # необходимые данные достаем из self.payment_params, self.paymethod_params, self.user_params здесь для
        # примера выводим параметры метода оплаты (self.paymethod_params) и платежа (self.payment_params) в лог

        # переводим платеж в статус оплачивается
        self.elid = uuid.uuid4()

        url = "https://api.yookassa.ru/v3/payments"

        auth = (store_id, secret_key)

        # Заголовки
        headers = {
            'Idempotence-Key': self.elid,
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

        response = requests.post(url, json=data, headers=headers, auth=auth).json()

        # url для перенаправления c cgi
        # здесь, в тестовом примере сразу перенаправляем на страницу BILLmanager
        # должны перенаправлять на страницу платежной системы

        payment.set_in_pay(str(self.elid), '', f'external_{response}')
        redirect_url = response['confirmation']['confirmation_url']

        # формируем html и отправляем в stdout
        # таким образом переходим на redirect_url
        payment_form = "<html>\n"
        payment_form += "<head><meta http-equiv='Content-Type' content='text/html; charset=UTF-8'>\n"
        payment_form += "<link rel='shortcut icon' href='billmgr.ico' type='image/x-icon' />"
        payment_form += "	<script language='JavaScript'>\n"
        payment_form += "		function DoSubmit() {\n"
        payment_form += "			window.location.assign('" + redirect_url + "');\n"
        payment_form += "		}\n"
        payment_form += "	</script>\n"
        payment_form += "</head>\n"
        payment_form += "<body onload='DoSubmit()'>\n"
        payment_form += "</body>\n"
        payment_form += "</html>\n"

        sys.stdout.write(payment_form)


logger.error('запущен testpayment TestPaymentCgi().Process()')
TestPaymentCgi().Process()
