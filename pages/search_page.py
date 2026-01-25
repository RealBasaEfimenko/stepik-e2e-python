import structlog
import time
from playwright.sync_api import Locator
from typing import Optional
from .base_page import BasePage

logger = structlog.get_logger(__name__)


class SearchPage(BasePage):
    """Page object для страницы результатов поиска Stepik (/catalog/search)"""

    @property
    def free_filter_button(self) -> Locator:
        """Кнопка фильтра 'Бесплатно' в сайдбаре"""
        return self.page.get_by_role("button", name="Бесплатно")

    @property
    def course_cards(self) -> Locator:
        """Все карточки курсов"""
        return self.page.locator("a.catalog-rich-card__link-wrapper")

    @property
    def first_course_card(self) -> Optional[Locator]:
        """Первая карточка курса(универсально)"""
        if self.course_cards.count() > 0:
            return self.course_cards.first
        return None

    def is_loaded(self) -> bool:
        """Проверка загрузки страницы результатов поиска."""
        self.log.info("Проверка загрузки страницы результатов" "")
        current_url = self.get_current_url()
        is_search_url = "/catalog/search" in current_url

        is_filter_visible = self.is_element_visible(self.free_filter_button, "Фильтр бесплатно")
        all_passed = is_search_url and is_filter_visible
        self.log.info(
            "Проверка загрузки завершения",
            is_search_url=is_search_url,
            is_filter_visible=is_filter_visible,
            all_passed=all_passed,
        )
        return all_passed

    def apply_free_filter(self) -> "SearchPage":
        """Применить фильтр 'Бесплатно'"""
        self.log.info("Применение фильтра 'Бесплатно'")

        self.click(self.free_filter_button, "Фильтр 'бесплатно'")
        self._wait_for_filter_applied()

        self.log.info("Фильтр 'Бесплатно' применен", current_url=self.get_current_url())
        return self

    def _wait_for_filter_applied(self) -> None:
        """Ожидание применения фильтра"""
        self.log.debug("Ожидание применения фильтра")

        self.wait_for_url("**free=true**", timeout=15000)
        time.sleep(1)
        self._wait_for_all_requests()
        self.log.debug("Фильтр успешно применен")

    def open_first_course(self) -> None:
        """Открыть первую карточку курса"""
        self.log.info("Открытие первого курса")

        # Проверяем, что есть хотя бы один курс
        if self.course_cards.count() == 0:
            self.log.error("Нет доступных курсов для открытия")
            raise ValueError("На странице нет карточек курсов")

        first_card = self.first_course_card
        if first_card:
            self.click(first_card, "Первая карточка курса")
            self.wait_for_url("**/course/**", 10000)

            self.log.info("Страница курса загружена")
        else:
            self.log.error("Первая карточка курса не найдена")
            raise ValueError("Не удалось найти первую карточку курса")
