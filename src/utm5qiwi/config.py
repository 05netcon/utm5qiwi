import os
import dotenv


dotenv.load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')

UTM_DB_NAME = os.getenv('UTM_DB_NAME')
OSMP_DB_NAME = os.getenv('OSMP_DB_NAME')

get_commands = ('check', 'pay')

get_headers = {
    'Content-Type': 'text/xml'
}

xml_templates = {
    'check': '''
        <?xml version='1.0' encoding='UTF-8'?>
        <response>
            <osmp_txn_id>{}</osmp_txn_id>
            <result>{}</result>
            <comment>{}</comment>
        </response>
    '''.strip(),
    'pay': '''
        <?xml version='1.0' encoding='UTF-8'?>
        <response>
            <osmp_txn_id>{}</osmp_txn_id>
            <prv_txn>{}</prv_txn>
            <sum>{}</sum>
            <result>{}</result>
            <comment>{}</comment>
        </response>
    '''.strip()
}

db_queries = {
    'account': '''
        SELECT users.basic_account
        FROM users 
        WHERE users.basic_account = '{}' AND users.is_deleted != 1
        LIMIT 1
    ''',
    'duplicate': '''
        SELECT `txn_id`, `check` 
        FROM osmp.temp 
        WHERE txn_id = '{}' AND `check` != '1' 
        LIMIT 1
    ''',
    'transact': '''
        SELECT payment_ext_number 
        FROM UTM5.payment_transactions 
        WHERE payment_ext_number = '{}' AND is_canceled != '1' 
        LIMIT 1
    ''',
    'save': '''
        INSERT INTO osmp.temp (`txn_id`, `account`, `sum`, `check`) 
        VALUES ('{}', '{}', '{}', '0')
    '''
}

pay_config = {
    'tool': '/netup/utm5/bin/utm5_payment_tool',
    'config': '/netup/utm5/utm5_payment_tool.cfg',
    'method': '101'
}

pay_command = '''{} -C {} -m {} -i'''.format(
    pay_config['tool'], 
    pay_config['config'], 
    pay_config['method']
) + ''' -b '{}' -a '{}' -e '{}' -t '{}' -L '{}' -k '{}' '''
