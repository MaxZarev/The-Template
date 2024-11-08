from __future__ import annotations

import functools
import os
import random
import secrets
import string
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Any

import requests
from eth_typing import ChecksumAddress
from web3 import Web3
from loguru import logger

from config.settings import config
from core.excel import Excel
from models.account import Account


def send_telegram_message(message: str) -> None:
    """
    Отправляет сообщение в телеграм
    :param message: текст сообщения
    :return: None
    """
    url = f'https://api.telegram.org/bot{config.bot_token}/sendMessage'
    params = {'chat_id': config.chat_id, 'text': message}
    requests.get(url, params=params)


def get_accounts() -> list[Account]:
    """
    Получает аккаунты из файла в зависимости от настроек в config
    :return: генератор аккаунтов
    """
    if config.accounts_source == 'excel':
        accounts_raw_data = get_from_excel()
    else:
        accounts_raw_data = get_accounts_from_txt()

    # Определяем количество аккаунтов
    length = len(accounts_raw_data[0])
    # Заполняем списки до нужной длины
    combined_data = filler(length, *accounts_raw_data)
    logger.info(f"Извлечено {length} аккаунтов")

    if config.is_random:
        # Перемешиваем данные
        random.shuffle(combined_data)

    # ленивый генератор аккаунтов
    for profile_number, password, private_key, seed, proxies in combined_data:
        yield Account(profile_number, password, private_key, seed, proxies)


def get_from_excel() -> tuple[list[str], list[str], list[str], list[str], list[str]]:
    """
    Получает аккаунты из excel файла
    :return: кортеж списков аккаунтов
    """
    excel = Excel()
    # Получаем данные из excel файла
    profile_numbers = excel.get_column("Profile Number")
    passwords = excel.get_column("Password")
    private_keys = excel.get_column("Seed")
    seeds = excel.get_column("Private Key")
    proxies = excel.get_column("Proxy")
    return profile_numbers, passwords, private_keys, seeds, proxies


def get_accounts_from_txt() -> tuple[list[str], list[str], list[str], list[str], list[str]]:
    """
    Достает данные из файлов и возвращает список аккаунтов
    :return: кортеж списков аккаунтов
    """
    # Получаем данные из файлов
    profile_numbers = get_list_from_file("profile_numbers.txt")
    passwords = get_list_from_file("passwords.txt")
    private_keys = get_list_from_file("private_keys.txt")
    seeds = get_list_from_file("seeds.txt")
    proxies = get_list_from_file("proxies.txt")
    return profile_numbers, passwords, private_keys, seeds, proxies


def filler(length: int, *_args: list[Any]) -> list[tuple[Any]]:
    """
    Заполняет список до нужной длины
    :param length: длина
    :param _args: список
    :return: заполненный список
    """
    for arg in _args:
        if not arg:
            arg = [None] * length
        if len(arg) < length:
            if len(arg) != 0:
                logger.warning('Проверьте файлы с данными, длина списков не совпадает')
            arg += [None] * (length - len(arg))

    return list(zip(*_args))


def get_list_from_file(
        name: str,
        check_empty: bool = False,
) -> list[str]:
    """
    Get list from file
    :param name: название файла с указанием расширения, файл должен находиться в папке config/data
    :param check_empty: проверять ли файл на пустоту
    :return: список строк из файла
    """
    file_path = os.path.join(config.PATH_DATA, name)

    if not os.path.exists(file_path):
        logger.error(f"Файл {name} не найден")
        exit(1)

    if check_empty and os.stat(file_path).st_size == 0:
        logger.error(f"Файл пустой: {file_path}")
        exit(1)

    with open(file_path, "r") as file:
        return file.read().splitlines()


def random_sleep(min_delay: float = 0.5, max_delay: float = 1.5) -> None:
    """
    Sleep random time
    :param min_delay: минимальное время задержки
    :param max_delay: максимальное время задержки
    :return: None
    """
    # если передали только min задержку, то max будет 10% больше
    if min_delay > max_delay:
        max_delay = min_delay * 1.1

    delay = random.uniform(min_delay, max_delay)  # Генерируем случайное число
    time.sleep(delay)  # Делаем перерыв


def generate_password(length_min: int = 25, length_max: int = 35) -> str:
    """
    Generate password
    :param length_min:
    :param length_max:
    :return:
    """
    length = random.randint(length_min, length_max)  # Генерируем случайную длину пароля

    # Определяем наборы символов
    all_characters = [string.ascii_uppercase, string.ascii_uppercase, string.digits, string.punctuation]

    # Обеспечиваем наличие хотя бы одного символа каждого типа
    password = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits),
        secrets.choice(string.punctuation)
    ]

    while len(password) < length:
        characters = secrets.choice(all_characters)
        password.append(secrets.choice(characters))

    # Перемешиваем пароль, чтобы сделать его менее предсказуемым
    random.shuffle(password)

    return ''.join(password)


def write_text_to_file(path: str, text: str) -> None:
    """
    Write string to file
    :param path: название файла
    :param text: текст
    """
    with open(path, "a") as file:
        file.write(text + "\n")


def get_response(
        url: str,
        params: Optional[dict] = None,
        attempts: int = 3,
        return_except: bool = True) -> Optional[dict]:
    """
    Делает get запрос и возвращает json из ответа
    :param url: ссылка для запроса
    :param params: параметры запроса
    :param attempts: количество попыток
    :param return_except: возвращать ли исключение
    :return: json из ответа
    """
    for _ in range(attempts):
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Ошибка get запроса, {url} {params} - {e}")
    if return_except:
        raise Exception(f"Ошибка get запроса, {url} {params}")
    return None


def to_checksum(address: str | ChecksumAddress) -> ChecksumAddress:
    """
    Преобразует адрес в checksum формат
    :param address: адрес
    :return: адрес в checksum формате
    """
    if isinstance(address, str):
        address = Web3.to_checksum_address(address)
    return address


def timeout(timeout):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(func, *args, **kwargs)
                return future.result(timeout=timeout)

        return wrapper

    return decorator
