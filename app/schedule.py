import requests
from datetime import *
from collections import defaultdict


order = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
today = datetime.today()
ds = today - timedelta(days=today.weekday())  # начало текущей недели
de = ds + timedelta(days=6)  # конец текущей недели


def schedule(group_id):
    sched = defaultdict(list)
    day = ''
    dateStart, dateEnd = str(ds)[0:10], str(de)[0:10]
    url = f'https://study.miigaik.ru/api/v1/group/{group_id}?dateStart={dateStart}&dateEnd={dateEnd}'
    # позже обработать респонсы на случай если расписание не найдено (например выходной или уже выпущенные группы)
    response = requests.get(url)
    data = response.json()

    week = sorted([i.capitalize() for i in data['schedule'].keys()], key=lambda d: order.index(d))

    def anti_shiz(value): # ТАБЛЭТКА ПРОТИВ ШИЗОИДНОГО РАСПРЕДЕЛЕНИЯ ФИО
        names = ''
        for fio in value:
            names += f'{fio['lastName']} {fio['firstName']} {fio['patronymic']} и '
        else:
            names = names[:-2]
        return names

    for days in week: # Перебираем по дням недели
        work_day = data['schedule'][days.lower()]

        for lesson in work_day:
            lsT, lsE = lesson['lessonStartTime'][:-3], lesson['lessonEndTime'][:-3]
            lsName, lsType, sg = lesson['disciplineName'], lesson['lessonType'], lesson['subgroup']
            teachers = anti_shiz(lesson['teachers'])
            crNumber, crFloor, crBuilding = lesson['classroomName'], lesson['classroomFloor'], lesson['classroomBuilding']

            day += (rf"""
{lsT} — {lsE}
    
{lsName} ({lsType}) \- {teachers}
{f'{sg}' if sg != '' else 'Общая пара'}, Ауд\. {crNumber} \(Этаж {crFloor}\, {crBuilding}\)


""")
        sched[days].append(day)
        day = ''
    return sched