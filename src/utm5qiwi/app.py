import logging
import subprocess

from datetime import datetime

import flask

from utm5qiwi import config
from utm5qiwi import helpers

from utm5qiwi.db.dbcm import UseDatabase


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = flask.Flask(__name__)

@app.route('/', methods=['GET'])
def api():
    # Переданные в GET запросе параметры должны пройти валидацию
    command = flask.request.args.get('command') or ''
    txn_id = flask.request.args.get('txn_id') or ''
    account = flask.request.args.get('account') or ''
    sum = flask.request.args.get('sum') or ''
    if not helpers.is_valid_number(txn_id): txn_id = ''
    if not helpers.is_valid_number(account): account = ''
    if not helpers.is_valid_number(sum): sum = ''
    if command in config.get_commands and txn_id and account and sum:
        db_config = {
            'host': config.DB_HOST,
            'database': config.UTM_DB_NAME,
            'user': config.DB_USER,
            'password': config.DB_PASS
        }
        with UseDatabase(db_config) as cursor:
            # Абонент с заданным номером лицевого счета
            # должен присутствовать в базе
            cursor.execute(config.db_queries['account'].format(account))
            db_data = cursor.fetchall()
        if db_data:
            if command == 'check':
                result = '0'
                comment = f'Лицевой счет {account} найден'
            else:
                # Нельзя допускать дублирование платежа
                # Проверяем по txn_id наличие этого платежа
                db_config['database'] = config.OSMP_DB_NAME
                with UseDatabase(db_config) as cursor:
                    cursor.execute(
                        config.db_queries['duplicate'].format(txn_id)
                    )
                    db_data = cursor.fetchall()
                if db_data:
                    result = '0'
                    comment = f'Платеж с txn_id {txn_id} ранее принят'
                else:
                    # В таком виде сохраняется идентификатор
                    # транзакции по платежу в базе UTM5
                    ee_data = f'OSMP{txn_id}'
                    current_date = datetime.strftime(
                        datetime.now(), "%Y%m%d%H%M%S"
                    )
                    pay_date = flask.request.args.get(
                        'txn_date'
                    ) or current_date
                    if not helpers.is_valid_date(pay_date):
                        pay_date = current_date
                    txn_date = helpers.get_mktime(pay_date)
                    pay_comment = f'Поступил платеж на сумму {sum} р.'
                    shell_cmd = config.pay_command.format(
                        sum,
                        account,
                        ee_data,
                        txn_date,
                        pay_comment,
                        pay_comment
                    )
                    subprocess.run(shell_cmd, shell=True, check=False)
                    # Необходимо убедиться, что в базе появились данные
                    # транзакции по последнему полученному платежу
                    db_config['database'] = config.UTM_DB_NAME
                    with UseDatabase(db_config) as cursor:
                        cursor.execute(
                            config.db_queries['transact'].format(ee_data)
                        )
                        db_data = cursor.fetchall()
                    if db_data:
                        db_config['database'] = config.OSMP_DB_NAME
                        with UseDatabase(db_config) as cursor:
                            cursor.execute(
                                config.db_queries['save'].format(
                                    txn_id, account, sum
                                )
                            )
                        prv_txn = cursor.lastrowid
                        result = '0'
                        comment = 'Платеж принят'
                    else:
                        result = '5'
                        comment = 'Транзакция по платежу не найдена'
        else:
            result = '5'
            comment = f'Лицевой счет {account} не найден'
    else:
        result = '300'
        comment = 'Переданные параметры запроса не верны'
    # Только результат с кодом 0 (ОК) является не критичным
    # В остальных случаях логируется сообщение об ошибке
    logger.warning(comment) if result else logger.info(comment)
    # При запросе на платеж (команда pay) переменная prv_txn
    # может быть не определена при определеных условиях
    if 'prv_txn' not in locals():
            prv_txn = '0'
    # Как при ошибке, так и при проверке лицевого счета
    # отправляется xml ответ формата check, иначе pay
    return (
        config.xml_templates['pay'].format(
            txn_id, prv_txn, sum, result, comment
        )
        if command == 'pay' else
        config.xml_templates['check'].format(txn_id, result, comment),
        200,
        config.get_headers,
    )


def main() -> None:
    app.run(debug=True, port=8080)

if __name__ == '__main__':
    main()

