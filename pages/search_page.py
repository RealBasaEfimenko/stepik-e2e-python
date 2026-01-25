import structlog
import time
import allure
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
        """Первая карточка курса (универсально)"""
        if self.course_cards.count() > 0:
            return self.course_cards.first
        return None

    def is_loaded(self) -> bool:
        """Проверка загрузки страницы результатов поиска."""
        self.log.info("Проверка загрузки страницы результатов")

        current_url = self.get_current_url()
        is_search_url = "/catalog/search" in current_url

        is_filter_visible = self.is_element_visible(self.free_filter_button, "Фильтр 'Бесплатно'")

        all_passed = is_search_url and is_filter_visible
        self.log.info(
            "Проверка загрузки завершена",
            is_search_url=is_search_url,
            is_filter_visible=is_filter_visible,
            all_passed=all_passed,
        )
        return all_passed

    @allure.step("Применение фильтра 'Бесплатно'")
    def apply_free_filter(self) -> "SearchPage":
        """Применить фильтр 'Бесплатно' и дождаться загрузки контента."""
        self.log.info("Применение фильтра 'Бесплатно'")

        # Кликаем на фильтр
        self.click(self.free_filter_button, "Фильтр 'Бесплатно'")

        # Ожидаем применения фильтра (динамическая загрузка)
        self._wait_for_filter_applied()

        # ВАЖНО: ДОЖДАТЬСЯ ПОЯВЛЕНИЯ КАРТОЧЕК
        self._wait_for_courses_to_load()

        self.log.info("Фильтр 'Бесплатно' применен", current_url=self.get_current_url())

        return self

    def _wait_for_filter_applied(self) -> None:
        """Ожидание применения фильтра."""
        self.log.debug("Ожидание применения фильтра")

        # Ждем обновления URL
        self.wait_for_url("**free=true**", timeout=15000)

        # Минимальная пауза для стабильности динамического контента
        time.sleep(1)
        self._wait_for_all_requests()

        self.log.debug("Фильтр успешно применен")

    def _wait_for_courses_to_load(self, timeout: int = 15000) -> None:
        """Ожидание загрузки карточек курсов после фильтрации."""
        self.log.info("Ожидание загрузки карточек курсов...")

        try:
            # Ждем появления хотя бы одной карточки
            self.page.wait_for_selector(
                "a.catalog-rich-card__link-wrapper",
                state="attached",  # Элемент появился в DOM
                timeout=timeout,
            )

            # Дополнительно: ждем, пока карточки станут видимыми
            self.page.wait_for_selector(
                "a.catalog-rich-card__link-wrapper",
                state="visible",  # Элемент видим на экране
                timeout=5000,
            )

            # Проверяем, что карточек больше 0
            cards_count = self.course_cards.count()
            self.log.info(f"Карточки курсов загружены. Найдено: {cards_count}")

        except Exception as e:
            self.log.error(f"Ошибка при ожидании карточек курсов: {e}")
            # Можно сделать скриншот для отладки
            self.take_screenshot("courses_not_loaded")
            raise

    @allure.step("Открытие первой карточки курса")
    def open_first_course(self) -> None:
        """Открыть первую карточку курса (упрощенный вариант для демо-проекта)."""
        self.log.info("Открытие первого курса")

        # 1. Находим первую карточку
        first_card = self.page.locator("a.catalog-rich-card__link-wrapper").first

        if first_card.count() == 0:
            self.log.error("Нет доступных курсов для открытия")
            raise ValueError("На странице нет карточек курсов")

        # 2. Запоминаем текущий URL (для логов)
        url_before = self.get_current_url()

        # 3. Кликаем (откроется новая вкладка)
        self.click(first_card, "Первая карточка курса")

        # 4. Даем время на открытие
        self.page.wait_for_timeout(2000)

        # 5. Логируем успех - клик прошел, курс открывается
        self.log.info(f"Клик выполнен. Открывается курс. URL до клика: {url_before}")
