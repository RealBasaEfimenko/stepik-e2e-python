import structlog
import allure
from playwright.sync_api import Locator
from typing import Optional
from .base_page import BasePage

logger = structlog.get_logger(__name__)


class CatalogPage(BasePage):
    """Page Object для главной страницы каталога Stepik (/catalog)"""

    @property
    def search_input(self) -> Locator:
        """Поле поиска на главной странице"""
        return self.page.get_by_placeholder("Название курса, автор или предмет")

    @property
    def search_button(self) -> Optional[Locator]:
        """Кнопка поиска (если есть)"""

        buttons = self.page.get_by_role("button", name="Искать")
        if buttons.count() > 0:
            return buttons.first
        return None

    def is_loaded(self) -> bool:
        """Проверка, что главная страница загрузилась"""

        self.log.info("Проверка загрузки главной страницы")

        is_search_visible = self.is_element_visible(self.search_input, "Поисковая старока")
        is_catalog_url = "/catalog" in self.get_current_url()

        self.log.info(
            "Проверка загрузки главной страницы завершена",
            search_visible=is_search_visible,
            is_catalog=is_catalog_url,
        )
        return is_search_visible and is_catalog_url

    @allure.step("Поиск курсов по запросу: {query}")
    def search_courses(self, query: str):
        """Поиск курсов по запросу

        Args:
            query: Поисковой запрос (например, ""python)
        Returns:
            Неявный переход на страницу результатов поиска
        """
        self.log.info("Поиск курсов", query=query)

        self.fill(self.search_input, query, "Поисковая строка")
        self.search_input.press("Enter")

        self.wait_for_url(f"**/catalog/search*", timeout=30000)
        self.wait_for_url(f"**q={query}*", timeout=15000)

        self.log.info("Поиск выполнен", query=query, current_url=self.get_current_url())

        from .search_page import SearchPage

        return SearchPage(self.page)
