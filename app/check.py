import re
import requests

def valid_group(data):
    mask = r'([1-9][0-9]{3})-([А-я]+)-([А-я]+)-(.+)'
    f_group = rf'{data[0]}-{data[1]}-{data[2]}'

    if re.match(mask, f_group):
        url = rf'https://study.miigaik.ru/api/v1/search/group?groupName={f_group}'
        response = requests.get(url)
        data = response.json()

        if data:
            return [_['id'] for _ in data][0]
        else:
            return 'Введенной группы не существует'
    else:
        return """Некорректно введена группа.
Формат должен быть такой: ГОД-БУКВЫ-БУКВЫ-(БУКВЫ/ЦИФРЫ)"""