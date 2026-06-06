import re
import asyncio
from dataclasses import dataclass

from aiogram import Router, Bot
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest


router = Router()

SEND_DELAY = 0.05

@dataclass
class MailingUser:
    telegram_id: int | str
    group_code: str
    is_mailing_enabled: bool

@dataclass
class ParsedGroup:
    year: str
    faculty: str
    specialty: str
    group: str
    course: int



def unsubscribe_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Отписаться от рассылки",
                    callback_data="mailing_unsubscribe"
                )
            ]
        ]
    )


# ============================================================
# КНОПКА "РАССЫЛКА"
# ============================================================

@router.callback_query(lambda f: f.data == "Рассылка")
async def mailing(callback: CallbackQuery):
    await callback.answer()

    user_id = callback.from_user.id

    user = await get_mailing_user(user_id)

    if not user:
        await callback.message.answer(
            "Не нашёл вашу группу. Проверьте корректность написания вашей группы."
        )
        return

    parsed_group = parse_group_code(user.group_code)

    await enable_user_mailing(user_id)

    await callback.message.answer(
        f"Рассылка включена.\n\n"
        f"Вы будете получать сообщения для:\n"
        f"• курса: {parsed_group.course}\n\n"
        f"• факультета: {parsed_group.faculty.upper()}\n"
        f"• специальности: {parsed_group.specialty.upper()}\n"
        f"• группы: {parsed_group.specialty.upper()}-{parsed_group.group.upper()}\n"
        f"Также будут приходить общие сообщения деканата.",
        reply_markup=unsubscribe_keyboard()
    )


@router.callback_query(lambda f: f.data == "mailing_unsubscribe")
async def mailing_unsubscribe(callback: CallbackQuery):
    await callback.answer()

    await disable_user_mailing(callback.from_user.id)

    await callback.message.answer(
        "Вы отписались от рассылки."
    )


# ============================================================
# ФУНКЦИЯ РАССЫЛКИ И СБОРА СТАТИСТИКИ
# ============================================================

async def send_smart_mailing(bot: Bot, text: str, source_type: str = "faculty") -> dict:
    """
    source_type="faculty":
        фильтруем по группе пользователя.

    source_type="dean_office":
        отправляем всем, у кого включена рассылка.
    """

    users = await get_all_mailing_users()

    success = 0
    skipped = 0
    failed = 0

    for user in users:
        if not user.is_mailing_enabled:
            skipped += 1
            continue

        try:
            parsed_group = parse_group_code(user.group_code)
        except ValueError:
            skipped += 1
            continue

        if not is_relevant_message(text=text, user_group=parsed_group, source_type=source_type):
            skipped += 1
            continue

        try:
            await bot.send_message(chat_id=user.telegram_id, text=text, reply_markup=unsubscribe_keyboard())
            success += 1

        except TelegramForbiddenError:
            failed += 1
            await disable_user_mailing(user.telegram_id)

        except TelegramBadRequest as error:
            failed += 1
            print(f"Ошибка отправки пользователю {user.telegram_id}: {error}")

        except Exception as error:
            failed += 1
            print(f"Неизвестная ошибка для {user.telegram_id}: {error}")

        await asyncio.sleep(SEND_DELAY)

    return {
        "success": success,
        "skipped": skipped,
        "failed": failed
    }


def normalize_text(text: str) -> str:
    return (
        text.lower()
        .replace("ё", "е")
        .replace("–", "-")
        .replace("—", "-")
        .replace("_", "-")
        .strip()
    )


def parse_group_code(group_code: str) -> ParsedGroup:
    """
    Ожидаемый формат названия группы:
    2025-фгииб-пи-1б
    """

    group_code = normalize_text(group_code)
    parts = group_code.split("-")

    if len(parts) != 4:
        raise ValueError(f"Неверный формат группы: {group_code}")

    year, faculty, specialty, group = parts

    course_match = re.search(r"\d+", group)

    if not course_match:
        raise ValueError(f"Не удалось определить курс из группы: {group}")

    return ParsedGroup(
        year=year,
        faculty=faculty,
        specialty=specialty,
        group=group,
        course=int(course_match.group())
    )


def is_relevant_message(text: str, user_group: ParsedGroup, source_type: str) -> bool:
    """
    Проверяет, нужно ли отправлять сообщение пользователю.

    dean_office:
        отправляем всем.

    faculty:
        отправляем, если сообщение подходит по:
        - году;
        - факультету;
        - специальности;
        - курсу;
        - полной группе.
    """

    if source_type == "dean_office":
        return True

    text = normalize_text(text)

    if not text:
        return False

    if has_full_group_name(text, user_group.specialty, user_group.group):
        return True

    if has_year(text, user_group.year):
        return True

    if has_faculty(text, user_group.faculty):
        return True

    if has_specialty(text, user_group.specialty):
        return True

    if has_course(text, user_group.course):
        return True

    return False


def has_year(text: str, year: str) -> bool:
    return bool(
        re.search(rf"\b{re.escape(year)}\b", text)
    )


def has_faculty(text: str, faculty: str) -> bool:
    faculty = normalize_text(faculty)

    return bool(
        re.search(rf"\b{re.escape(faculty)}\b", text)
    )


def has_specialty(text: str, specialty: str) -> bool:

    specialty = normalize_text(specialty)

    return bool(
        re.search(rf"\b{re.escape(specialty)}\b", text)
    )


def has_course(text: str, course: int) -> bool:
    course_words = {
        1: [
            "первый", "первого", "первому", "первым", "первом",
            "первые", "первых", "первыми"
        ],
        2: [
            "второй", "второго", "второму", "вторым", "втором",
            "вторые", "вторых", "вторыми"
        ],
        3: [
            "третий", "третьего", "третьему", "третьим", "третьем",
            "третьи", "третьих", "третьими"
        ],
        4: [
            "четвертый", "четвертого", "четвертому", "четвертым", "четвертом",
            "четвертые", "четвертых", "четвертыми",
            "четвёртый", "четвёртого", "четвёртому", "четвёртым", "четвёртом",
            "четвёртые", "четвёртых", "четвёртыми"
        ],
        5: [
            "пятый", "пятого", "пятому", "пятым", "пятом",
            "пятые", "пятых", "пятыми"
        ],
    }

    course_forms = [
        "курс", "курса", "курсу", "курсом", "курсе",
        "курсы", "курсов", "курсам", "курсами", "курсах"
    ]

    patterns = []

    for course_form in course_forms:
        patterns.append(rf"\b{course}\s*{course_form}\b")
        patterns.append(rf"\b{course}\s*-\s*й\s*{course_form}\b")
        patterns.append(rf"\b{course}й\s*{course_form}\b")

    for word in course_words.get(course, []):
        for course_form in course_forms:
            patterns.append(rf"\b{word}\s+{course_form}\b")

    return any(
        re.search(pattern, text)
        for pattern in patterns
    )


def has_full_group_name(text: str, specialty: str, group: str) -> bool:

    specialty = normalize_text(specialty)
    group = normalize_text(group)

    pattern = rf"\b{re.escape(specialty)}\s*[-_/ ]?\s*{re.escape(group)}\b"

    return bool(
        re.search(pattern, text)
    )


async def get_mailing_user(telegram_id: int | str) -> MailingUser | None:
    """
    Достать одного пользователя из БД.

    Нужно вернуть:
    - telegram_id
    - group_code
    - is_mailing_enabled
    """



    return None


async def get_all_mailing_users() -> list[MailingUser]:
    """
    Достать всех пользователей, которые могут получать рассылку.

    Лучше сразу выбирать только тех, у кого рассылка включена:

    SELECT telegram_id, group_code, is_mailing_enabled
    FROM users WHERE is_mailing_enabled = 1
    """

    return []


async def enable_user_mailing(telegram_id: int | str) -> None:
    """
    Включить рассылку пользователю.

    UPDATE users
    SET is_mailing_enabled = 1
    WHERE telegram_id = ?
    """

    pass


async def disable_user_mailing(telegram_id: int | str) -> None:
    """
    Выключить рассылку пользователю.

    UPDATE users
    SET is_mailing_enabled = 0
    WHERE telegram_id = ?
    """

    pass