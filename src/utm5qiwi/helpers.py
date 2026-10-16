import datetime

from zoneinfo import ZoneInfo


def get_mktime(string: str) -> int:
    '''
    Функция, возвращает дату в формате timestamp полученную
    из строки входного параметра в формате YYYYMMDDHHMMSS
    '''
    if string:
        year = int(string[:4])
        month = int(string[4:6])
        day = int(string[6:8])
        hour = int(string[8:10])
        minute = int(string[10:12])
        second = int(string[12:])
        return int(datetime.datetime(
            year,
            month,
            day,
            hour,
            minute,
            second,
            tzinfo=ZoneInfo(key='Europe/Moscow'),
        ).timestamp())
    else:
        return 0

def is_valid_number(value: str) -> bool:
    '''
    Функция проверяет валидность входного параметра
    Параметр должен соответствовать целым и дробным числам
    '''
    if value.isdigit():
        if int(value) > 0:
            return True
    else:
        try:
            if float(value) > 0:
                return True
        except ValueError:
            return False
    return False

def is_valid_date(value: str) -> bool:
    '''
    Функция проверяет валидность входного параметра
    Параметр должен быть длиной 14 символов и состоять только из цифр
    '''
    if len(value) == 14 and value.isdigit():
        return True
    return False
