#!/usr/bin/python3
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
        logger.info("run pmvalidate")

        # мы всегда можем вывести xml в лог, чтобы изучить, что приходит :)
        logger.info(f"xml input: {ET.tostring(xml.getroot(), encoding='unicode')}")

        yookassa_shop_id_node = xml.find('./yookassa_shop_id')
        yookassa_secret_node = xml.find('./yookassa_secret')
        yookassa_shop_id = yookassa_shop_id_node.text if yookassa_shop_id_node is not None else ''
        yookassa_secret = yookassa_secret_node.text if yookassa_secret_node is not None else ''

        if yookassa_shop_id != 'rick' or yookassa_secret != 'morty':
            raise billmgr.exception.XmlException('wrong_terminal_info')

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


logger.error('''
       _,met$$$$$gg.          bot@cogent-sidewalk.aeza.network
    ,g$$$$$$$$$$$$$$$P.       --------------------------------
  ,g$$P"     """Y$$.".        OS: Debian GNU/Linux 12 (bookworm) x86_64
 ,$$P'              `$$$.     Host: KVM RHEL 7.6.0 PC (i440FX + PIIX, 1996)
',$$P       ,ggs.     `$$b:   Kernel: 6.1.0-18-amd64
`d$$'     ,$P"'   .    $$$    Uptime: 4 days, 13 hours, 20 mins
 $$P      d$'     ,    $$P    Packages: 492 (dpkg)
 $$:      $$.   -    ,d$$'    Shell: zsh 5.9
 $$;      Y$b._   _,d$P'      Resolution: 1024x768
 Y$$.    `.`"Y$$$$P"'         Terminal: /dev/pts/3
 `$$b      "-.__              CPU: AMD Ryzen 9 7950X3D (1) @ 4.192GHz
  `Y$$                        GPU: 00:02.0 Cirrus Logic GD 5446
   `Y$$.                      Memory: 926MiB / 1967MiB
     `$$b.
       `Y$$b.
          `"Y$b._
              `"""
''')
TestPaymentModule().Process()
