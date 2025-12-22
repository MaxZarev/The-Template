from abc import ABC, abstractmethod
from playwright.sync_api import Locator

from core.browser.ads import Ads
from core.excel import Excel
from models.account import Account
from models.chain import Chain


class Wallet(ABC):
    """
    Абстрактный базовый класс для работы с криптокошельками в браузере
    """

    def __init__(self, ads: Ads, account: Account, excel: Excel) -> None:
        self._url = None
        self.ads = ads
        self.password = account.password
        self.seed = account.seed
        self.excel = excel

    @abstractmethod
    def open_wallet(self):
        """Открывает кошелек"""
        pass

    @abstractmethod
    def create_wallet(self, save_in_excel: bool = False) -> tuple[str, str, str]:
        """Создает новый кошелек"""
        pass

    @abstractmethod
    def auth_wallet(self) -> None:
        """Авторизуется в кошельке"""
        pass

    @abstractmethod
    def import_wallet(self) -> tuple[str, str, str]:
        """Импортирует кошелек по seed-фразе"""
        pass

    @abstractmethod
    def get_address(self) -> str:
        """Возвращает адрес кошелька"""
        pass

    @abstractmethod
    def connect(self, locator: Locator, timeout: int = 30) -> None:
        """Подтверждает подключение кошелька к dApp"""
        pass

    @abstractmethod
    def sign(self, locator: Locator, timeout: int = 30) -> None:
        """Подтверждает подпись сообщения"""
        pass

    @abstractmethod
    def send_tx(self, locator: Locator, timeout: int = 30) -> None:
        """Подтверждает отправку транзакции"""
        pass

    @abstractmethod
    def select_chain(self, chain: Chain) -> None:
        """Выбирает сеть в кошельке"""
        pass

    @abstractmethod
    def set_chain(self, chain: Chain) -> None:
        """Добавляет новую сеть в кошелек"""
        pass

    @abstractmethod
    def change_chain_data(self, chain: Chain) -> None:
        """Изменяет параметры существующей сети"""
        pass

    @abstractmethod
    def universal_confirm(self, windows: int = 1, buttons: int = 1) -> None:
        """Универсальное подтверждение действий в кошельке"""
        pass
