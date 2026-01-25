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
        Польный пользовательский сценарий:
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

        login_page.login(credentials["login"], credentials["password"])

        assert login_page.is_login_successful(), "Авторизация не удалась. Кнопка профиля не видна"

        assert catalog_page.is_loaded(), "Главная страница не загрузилась после авторизации"

        search_page = catalog_page.search_courses("python")

        assert search_page.is_loaded(), "Страница результатов поиска не загрузилась"
        search_page.apply_free_filter()
        search_page.open_first_course()

        final_url = page.url
        assert "/course/" in final_url, f"Не першли на страницу куса. Финальный URL: {final_url}"

        assert page.title(), "Страница курса не имеет загаловка"
