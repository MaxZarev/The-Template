# Гайд: Как добавить новый кошелек

Этот гайд описывает пошаговый процесс добавления нового криптокошелька (например, Phantom, Rabby, Trust Wallet и т.д.) в проект.

## Архитектура

Все кошельки наследуются от абстрактного класса `Wallet` (`wallet.py`), который определяет единый интерфейс для работы с любым кошельком. Это обеспечивает:

- Единообразие API
- Полиморфизм (можно работать с разными кошельками через один интерфейс)
- Контроль реализации всех необходимых методов

---

## Шаг 1: Создайте новый файл кошелька

Создайте новый Python-файл в директории `core/browser/wallets/` с названием вашего кошелька в нижнем регистре, например:

- `phantom.py` - для Phantom Wallet
- `rabby.py` - для Rabby Wallet
- `trust_wallet.py` - для Trust Wallet

---

## Шаг 2: Импортируйте необходимые модули

В начале файла добавьте импорты:

```python
import re  # если нужна работа с регулярными выражениями

from loguru import logger
from playwright.sync_api import Locator

from core.browser.ads import Ads
from core.browser.wallets.wallet import Wallet
from core.excel import Excel
from config import config
from models.account import Account
from models.chain import Chain
from utils.utils import random_sleep, generate_password
```

---

## Шаг 3: Создайте класс, наследующий Wallet

```python
class YourWallet(Wallet):
    """
    Класс для работы с YourWallet v. X.X.X
    """

    def __init__(self, ads: Ads, account: Account, excel: Excel) -> None:
        super().__init__(ads, account, excel)
        # Добавьте URL вашего кошелька в config/settings.py
        self._url = config.your_wallet_url
```

**Важно:**

- Замените `YourWallet` на название вашего кошелька (например, `Phantom`)
-
- Обязательно вызовите `super().__init__(ads, account, excel)`
- Настройте URL расширения кошелька в `config/settings.py`, создав переменную с названием вашего кошелька (например, `metamask_url`)
- Указывайте версию расширения с которой работает скрипт

---

## Шаг 4: Реализуйте все абстрактные методы

Класс `Wallet` определяет 11 абстрактных методов, которые **обязательно** нужно реализовать:

### 4.1. `open_wallet()`

Открывает страницу расширения кошелька.

```python
def open_wallet(self):
    """
    Открывает YourWallet
    :return:
    """
    self.ads.open_url(self._url)
    random_sleep(3, 4)
```

### 4.2. `create_wallet(save_in_excel: bool = False)`

Создает новый кошелек с нуля, генерирует seed-фразу и пароль.

```python
def create_wallet(self, save_in_excel: bool = False) -> tuple[str, str, str]:
    """
    Создает кошелек в YourWallet
    :param save_in_excel: если True, сохраняет данные в Excel
    :return: tuple (address, seed, password)
    """
    self.open_wallet()

    # 1. Кликните по кнопке создания кошелька
    # 2. Сгенерируйте или введите пароль
    if not self.password:
        self.password = generate_password()

    # 3. Получите seed-фразу
    # 4. Подтвердите seed-фразу
    # 5. Получите адрес кошелька
    address = self.get_address()

    # 6. Сохраните в Excel если нужно
    if save_in_excel:
        self.excel.set_cell('Address', address)
        self.excel.set_cell('Seed', seed_str)
        self.excel.set_cell('Password', self.password)

    return address, seed_str, self.password
```

### 4.3. `auth_wallet()`

Авторизуется в кошельке по паролю.

```python
def auth_wallet(self) -> None:
    """
    Авторизуется в YourWallet
    :return: None
    """
    self.open_wallet()

    if not self.password:
        raise Exception(
            f'{self.ads.profile_number} не указан пароль для авторизации')

    try:
        # Найдите поле пароля и кнопку входа
        # self.ads.page.locator('#password').fill(str(self.password))
        # self.ads.page.locator('button[type="submit"]').click()
        random_sleep(3, 5)
        logger.info(f'{self.ads.profile_number} успешно авторизован')
    except Exception as e:
        logger.error(f'{self.ads.profile_number} ошибка авторизации: {e}')
```

### 4.4. `import_wallet()`

Импортирует существующий кошелек по seed-фразе.

```python
def import_wallet(self) -> tuple[str, str, str]:
    """
    Импортирует кошелек в YourWallet
    :return: tuple (address, seed, password)
    """
    self.open_wallet()

    seed_list = self.seed.split(' ')
    if not self.password:
        self.password = generate_password()

    # 1. Найдите кнопку импорта
    # 2. Введите seed-фразу
    # 3. Создайте/введите пароль
    # 4. Подтвердите импорт

    address = self.get_address()
    seed_str = ' '.join(seed_list)
    return address, seed_str, self.password
```

### 4.5. `get_address()`

Получает адрес активного кошелька.

```python
def get_address(self) -> str:
    """
    Возвращает адрес кошелька
    :return: адрес кошелька
    """
    # Найдите элемент с адресом и извлеките его
    # address = self.ads.page.locator('.wallet-address').inner_text()
    # return address.strip()
    pass
```

### 4.6. `connect(locator: Locator, timeout: int = 30)`

Подтверждает подключение кошелька к dApp.

```python
def connect(self, locator: Locator, timeout: int = 30) -> None:
    """
    Подтверждает подключение к dApp
    :param locator: локатор кнопки подключения
    :param timeout: время ожидания в секундах
    :return: None
    """
    try:
        # Ловим всплывающее окно кошелька
        with self.ads.context.expect_page(timeout=timeout * 1000) as page_catcher:
            locator.click()
        wallet_page = page_catcher.value
    except Exception as e:
        logger.warning(f'{self.ads.profile_number} не удалось поймать окно: {e}')
        wallet_page = self.ads.catch_page(['notification', 'connect'])
        if not wallet_page:
            raise Exception(f'{self.ads.profile_number} Ошибка подключения')

    wallet_page.wait_for_load_state('load')
    # Найдите кнопку подтверждения и кликните
    # wallet_page.locator('button.approve').click()
```

### 4.7. `sign(locator: Locator, timeout: int = 30)`

Подтверждает подпись сообщения.

```python
def sign(self, locator: Locator, timeout: int = 30) -> None:
    """
    Подтверждает подпись сообщения
    :param locator: локатор кнопки вызова подписи
    :param timeout: время ожидания в секундах
    :return: None
    """
    # Аналогично connect(), но для подписи сообщений
    pass
```

### 4.8. `send_tx(locator: Locator, timeout: int = 30)`

Подтверждает отправку транзакции.

```python
def send_tx(self, locator: Locator, timeout: int = 30) -> None:
    """
    Подтверждает отправку транзакции
    :param locator: локатор кнопки вызова транзакции
    :param timeout: время ожидания в секундах
    :return: None
    """
    # Аналогично connect(), но для транзакций
    pass
```

### 4.9. `select_chain(chain: Chain)`

Переключает активную сеть в кошельке.

```python
def select_chain(self, chain: Chain) -> None:
    """
    Выбирает сеть в кошельке
    :param chain: объект сети Chain
    :return: None
    """
    self.open_wallet()

    # 1. Откройте меню выбора сети
    # 2. Проверьте, есть ли нужная сеть
    # 3. Если есть - выберите её
    # 4. Если нет - добавьте через set_chain()
```

### 4.10. `set_chain(chain: Chain)`

Добавляет новую сеть в кошелек.

```python
def set_chain(self, chain: Chain) -> None:
    """
    Добавляет новую сеть в кошелек
    :param chain: объект сети
    """
    # 1. Откройте настройки сетей
    # 2. Заполните поля:
    #    - Название: chain.metamask_name (или свой атрибут)
    #    - RPC URL: chain.rpc
    #    - Chain ID: chain.chain_id
    #    - Символ: chain.native_token
    # 3. Сохраните
```

### 4.11. `change_chain_data(chain: Chain)`

Изменяет параметры существующей сети.

```python
def change_chain_data(self, chain: Chain) -> None:
    """
    Изменяет параметры существующей сети
    :param chain: объект сети с новыми параметрами
    """
    # 1. Найдите сеть по chain_id
    # 2. Откройте её настройки
    # 3. Обновите параметры
    # 4. Сохраните
```

### 4.12. `universal_confirm(windows: int = 1, buttons: int = 1)`

Универсальное подтверждение любых действий.

```python
def universal_confirm(self, windows: int = 1, buttons: int = 1) -> None:
    """
    Универсальное подтверждение действий
    :param windows: количество окон
    :param buttons: количество кнопок подтверждения
    """
    for _ in range(windows):
        random_sleep(2, 3)
        page = self.ads.context.new_page()
        page.goto(self._url)

        # Попробуйте найти и нажать кнопки подтверждения
        confirm_buttons = ['button.confirm', 'button.approve', ...]
        for __ in range(buttons):
            for selector in confirm_buttons:
                if page.locator(selector).count():
                    page.locator(selector).click()
                    logger.info(f'{self.ads.profile_number} Подтверждено')
                    break
        page.close()
```

---

## Шаг 5: Добавьте URL кошелька в config

В файле `config/settings.py` добавьте URL расширения:

```python
class Config:
    # ... существующие настройки ...

    metamask_url = 'chrome-extension://...'
    your_wallet_url = 'chrome-extension://...'  # Добавьте ваш URL
```

**Как найти URL расширения:**

1. Откройте браузер с установленным расширением
2. Перейдите в `chrome://extensions/`
3. Включите "Режим разработчика"
4. Скопируйте ID расширения
5. URL будет: `chrome-extension://{ID}/home.html` (или другая страница)

---

## Шаг 6: Зарегистрируйте кошелек в **init**.py

Откройте `core/browser/wallets/__init__.py` и добавьте:

```python
from core.browser.wallets.wallet import Wallet
from core.browser.wallets.metamask import Metamask
from core.browser.wallets.your_wallet import YourWallet  # Добавьте

__all__ = ['Wallet', 'Metamask', 'YourWallet']  # Добавьте
```

---

## Шаг 7: Экспортируйте из core.browser

Откройте `core/browser/__init__.py` и добавьте:

```python
from core.browser.ads import Ads
from core.browser.wallets import Wallet, Metamask, YourWallet  # Добавьте

__all__ = ['Ads', 'Wallet', 'Metamask', 'YourWallet']  # Добавьте
```

---

## Шаг 8: Используйте новый кошелек

Теперь можно использовать новый кошелек в коде:

```python
from core.browser import Ads, YourWallet
from core.excel import Excel
from models.account import Account

# Создание экземпляра
ads = Ads(profile_number=1, proxy=None)
account = Account(password="pass123", seed="seed phrase here")
excel = Excel()

wallet = YourWallet(ads, account, excel)

# Использование
wallet.auth_wallet()
address = wallet.get_address()
```

Или через полиморфизм:

```python
def process_wallet(wallet: Wallet):
    """Работает с любым кошельком"""
    wallet.open_wallet()
    wallet.auth_wallet()
    return wallet.get_address()

# Использование
metamask = Metamask(ads, account, excel)
your_wallet = YourWallet(ads, account, excel)

process_wallet(metamask)      # Работает!
process_wallet(your_wallet)   # Тоже работает!
```

---

## Шаг 9: Добавьте кошелек в Bot класс

В классе `Bot` (`core/bot.py`) можно одновременно инициализировать несколько кошельков и использовать нужный в зависимости от задачи.

### Текущая реализация Bot класса:

```python
class Bot:
    def __init__(self, account: Account, chain: Chain = config.start_chain) -> None:
        logger.info(f'{account.profile_number} Запуск профиля')
        self.chain = chain
        self.account = account
        self.ads = Ads(account)
        self.excel = Excel(account)
        self.metamask = Metamask(self.ads, account, self.excel)  # ← MetaMask уже добавлен
        self.exchanges = Exchanges(account)
        self.onchain = Onchain(account, self.chain)
```

### Добавление нового кошелька вместе с MetaMask:

Чтобы иметь доступ к нескольким кошелькам одновременно, добавьте импорт и инициализацию:

```python
from core.browser import Ads, Metamask, YourWallet  # Импортируйте новый кошелек

class Bot:
    def __init__(self, account: Account, chain: Chain = config.start_chain) -> None:
        logger.info(f'{account.profile_number} Запуск профиля')
        self.chain = chain
        self.account = account
        self.ads = Ads(account)
        self.excel = Excel(account)

        # Инициализируем несколько кошельков
        self.metamask = Metamask(self.ads, account, self.excel)
        self.your_wallet = YourWallet(self.ads, account, self.excel)  # ← Добавьте свой кошелек

        self.exchanges = Exchanges(account)
        self.onchain = Onchain(account, self.chain)
```

### Использование в скриптах:

**Простое использование:**

```python
from core.bot import Bot
from models.account import Account

account = Account(...)

with Bot(account) as bot:
    # Используйте MetaMask
    bot.metamask.auth_wallet()
    metamask_address = bot.metamask.get_address()

    # Или используйте YourWallet
    bot.your_wallet.auth_wallet()
    your_wallet_address = bot.your_wallet.get_address()

    # Подключение MetaMask к dApp
    connect_button = bot.ads.page.locator('button.connect-wallet')
    bot.metamask.connect(connect_button)

    # Или подключение YourWallet к другому dApp
    another_button = bot.ads.page.locator('button.connect')
    bot.your_wallet.connect(another_button)
```

**Пример реального скрипта с несколькими кошельками:**

```python
from core.bot import Bot
from models.account import Account
from config.chains import Chains

account = Account(...)

with Bot(account) as bot:
    # Авторизуемся в MetaMask
    bot.metamask.auth_wallet()
    bot.metamask.select_chain(Chains.ARBITRUM)

    # Открываем dApp
    bot.ads.open_url('https://example-dapp.com')

    # Подключаем MetaMask
    connect_btn = bot.ads.page.locator('button:has-text("Connect MetaMask")')
    bot.metamask.connect(connect_btn)

    # Делаем swap через MetaMask
    swap_btn = bot.ads.page.locator('button:has-text("Swap")')
    bot.metamask.send_tx(swap_btn)

    # Если у dApp есть опция подключить второй кошелек
    bot.your_wallet.auth_wallet()
    bot.your_wallet.select_chain(Chains.OPTIMISM)

    another_connect_btn = bot.ads.page.locator('button:has-text("Add Wallet")')
    bot.your_wallet.connect(another_connect_btn)
```

### Важно:

- Все кошельки работают в одном браузерном контексте (`self.ads`)
- Можно переключаться между кошельками в рамках одной сессии
- Каждый кошелек имеет свой URL расширения (настроенный в config)
- Методы кошельков не конфликтуют друг с другом благодаря полиморфизму
- Простой доступ через `bot.metamask` и `bot.your_wallet`

---

## Тестирование

После реализации протестируйте:

1. **Создание кошелька**: `wallet.create_wallet()`
2. **Импорт кошелька**: `wallet.import_wallet()`
3. **Авторизация**: `wallet.auth_wallet()`
4. **Получение адреса**: `wallet.get_address()`
5. **Подключение к dApp**: `wallet.connect(locator)`
6. **Отправка транзакции**: `wallet.send_tx(locator)`
7. **Переключение сети**: `wallet.select_chain(chain)`

---

## Пример готового кошелька

См. `metamask.py` как reference implementation всех методов.

---

## Возникли вопросы?

- Изучите реализацию `Metamask` в `metamask.py`
- Используйте playwright inspector для отладки селекторов
- Проверьте логи через `logger`
- Скормите этот файл ИИ помощнику, чтобы он подсказал что делать

Удачи в разработке! 🚀
