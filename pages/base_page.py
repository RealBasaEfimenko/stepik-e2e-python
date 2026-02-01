import structlog
import os
from playwright.sync_api import Page, Locator, Response
from typing import Optional

logger = structlog.get_logger(__name__)


class BasePage:
    """Базовый класс для всех страниц с логгированием"""

    def __init__(self, page: Page, timeout: float = 30000) -> None:
        """Инициализация страницы

        Args:
            page (Page): Экземпляр страницы Playwright
            timeout (float, optional): Таймаут ожидания по умолчанию. Defaults to 30000
        """
        self.page = page
        self.timeout = timeout
        self.log = logger.bind(page_url=self.page.url)
        self.log.info("Инициализирована страница", timeout=timeout)

    def _wait_for_all_requests(self) -> None:
        """
        Ожидать завершения всех сетевых запросов
        """
        self.log.debug("Ожидание завершения сетевых запросов.")
        self.page.wait_for_load_state("domcontentloaded")

    def navigate(self, url: str) -> Optional[Response]:
        """
        Переход по URL с логированием


        :param url: Полный URL для перехода
        :return: Response object или None

        """
        self.log.info("Навигация по URL", url=url)
        response = self.page.goto(url, wait_until="networkidle", timeout=self.timeout)
        return response

    def click(self, locator: Locator, element_description: str) -> None:
        """Клик по элементу с ожиданием и логированием

        Args:
            locator : Локатор playwright
            element_description (str): Человекочитаемое описание элемента для логов
        """
        self.log.info(f"Клик по элементу, {element_description}")

        locator.click(timeout=self.timeout)
        self._wait_for_all_requests()

        self.log.info(f"Успешный клик: {element_description}", current_url=self.page.url)

    def fill(self, locator: Locator, text: str, element_description: str) -> None:
        """Заполнение поля с логированием

        Args:
            locator: Локтор Playwright
            text: Текст для ввода
            element_description: Описание поля
        """
        self.log.info(
            f"Заполняю поля: {element_description}",
            text=text[:10] + "..." if len(text) > 10 else text,
        )

        locator.fill(text, timeout=self.timeout)
        self.log.info(f"Поле заполнено: {element_description}")

    def get_current_url(self) -> str:
        """
        Получить текущий URL с логированием

        :return: URL страницы
        """
        url = self.page.url
        self.log.debug("Текущий URL", url=url)
        return url

    def wait_for_url(self, url_pattern: str, timeout: Optional[float]) -> None:
        """
        Ожидание перехода на URL по паттерну

        :param url_pattern: Паттерн URL для ожидания(может быть частью URL)
        :param timeout: Кастомный таймаут
        """
        timeout = self.timeout if timeout is None else timeout
        self.log.info("Ожидание URL", pattern=url_pattern)

        try:
            self.page.wait_for_url(url_pattern, timeout=timeout)
            self.log.info("URL обнаружен", pattern=url_pattern, current_url=self.page.url)
        except Exception as e:
            self.log.error(
                "URL не обнаружен", pattern=url_pattern, current_url=self.page.url, error=str(e)
            )
            raise

    def is_element_visible(self, locator: Locator, element_description: str) -> bool:
        """
        Проверка видимости элемента

        Args:
            locator: Локатор Playwright
            element_description: Описание элемента
        """
        try:
            is_visible = locator.is_visible(timeout=5000)
            self.log.debug(f"Видимость элемента '{element_description}'", is_visible=is_visible)
            return is_visible
        except Exception as e:
            self.log.debug(f"Элемент '{element_description}' не найден", error=str(e))
            return False

    def take_screenshot(self, name: str) -> None:
        screenshot_path = f"screenshots/{name}.png"
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        self.page.screenshot(path=screenshot_path)
        self.log.info("Скриншот сохранен", path=screenshot_path)
