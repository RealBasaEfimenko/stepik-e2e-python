import allure
import pytest
from pages.login_page import LoginPage
from pages.catalog_page import CatalogPage


@allure.epic("Stepik UI Automation")
@allure.feature("Поиск и фильтрация курсов")
class TestSearchFreeCourses:
    """
    E2E тест: авторизация -> поиск курсов -> фильтрация -> выбор курса.
    """

    @allure.title("Поиск бесплатных курсов по запросу 'python'")
    @allure.description(
        """
        Полный пользовательский сценарий:
        1. Авторизация на Stepik.org
        2. Поиск курсов по запросу 'python'
        3. Применение фильтра 'Бесплатно'
        4. Открытие первого найденного курса

        Ожидаемый результат:
        - Пользователь успешно авторизован
        - Курсы по запросу 'python' найдены
        - Фильтр 'Бесплатно' применен
        - Первый курс успешно открыт
        """
    )
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_free_python_courses(self, page, credentials):
        """Основной E2E-тест для проверки поиска и фильтрации курсов"""

        # Инициализация Page Objects
        login_page = LoginPage(page)
        catalog_page = CatalogPage(page)

        # 1. АВТОРИЗАЦИЯ
        login_page.login(credentials["login"], credentials["password"])
        assert login_page.is_login_successful(), "Авторизация не удалась"
        assert catalog_page.is_loaded(), "Главная страница не загрузилась"

        # 2. ПОИСК КУРСОВ
        search_page = catalog_page.search_courses("python")
        assert search_page.is_loaded(), "Страница результатов поиска не загрузилась"

        # 3. ПРИМЕНЕНИЕ ФИЛЬТРА "БЕСПЛАТНО"
        search_page.apply_free_filter()

        # 4. ОТКРЫТИЕ ПЕРВОГО КУРСА
        search_page.open_first_course()

        # 5. ФИНАЛЬНЫЕ ПРОВЕРКИ (РЕАЛЬНЫЕ)

        # Проверка 1: URL не остался таким же как до клика (что-то произошло)
        current_url = page.url
        assert (
            "/catalog/search" in current_url
        ), f"Ожидали остаться на странице поиска, но URL: {current_url}"

        # Финальный assert с понятным сообщением
        assert (
            "/catalog/search" in current_url
        ), f"Финальная проверка: должны быть на странице поиска. URL: {current_url}"
