# Пусть смотрит расписание двух недель группы и оттуда берёт все ФИО преподов
# Контакты этих же преподов и высвечиваются
import requests
from datetime import *
import database.requests as rq


group_teachers = set()

today = datetime.today()
ds = today - timedelta(days=today.weekday())  # начало текущей недели
de = ds + timedelta(days=6)  # конец текущей недели

ds_prev = today - timedelta(days=today.weekday() + 7)

datePrevStart, dateEnd = str(ds_prev)[0:10], str(de)[0:10]

async def teach_contact(group_id):
    url = f'https://study.miigaik.ru/api/v1/group/{group_id}?dateStart={datePrevStart}&dateEnd={dateEnd}'
    response = requests.get(url)
    data = response.json()

    for i in data['schedule'].values():
        for k in [_['teachers'] for _ in i]:
            group_teachers.add(' '.join(k[0].values()))

    res = []

    for contact in group_teachers:
        info = await rq.get_contacts(contact)
        res.append(info)
        break
    message = ''

    for name in res[0]:
        message += (f'''{name[0]} - {name[1]}
{name[2]} | {name[3]}

''')


    return f'{message}' if message else 'Контактов твоей группы не нашлось'