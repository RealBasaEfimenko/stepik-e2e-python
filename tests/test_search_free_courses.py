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
        - Первый курс успешно открыт и отображается
        """
    )
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.flaky(reruns=1, reruns_delay=2)
    def test_search_free_python_courses(self, page, credentials):
        """Основной E2E-тест для проверки поиска и фильтрации курсов"""

        # Инициализация Page Objects
        login_page = LoginPage(page)
        catalog_page = CatalogPage(page)

        # 1. АВТОРИЗАЦИЯ
        with allure.step("1. Авторизация пользователя"):
            login_page.login(credentials["login"], credentials["password"])
            assert login_page.is_login_successful(), "Авторизация не удалась"
            assert catalog_page.is_loaded(), "Главная страница не загрузилась"

        # 2. ПОИСК КУРСОВ
        with allure.step("2. Поиск курсов по запросу 'python'"):
            search_page = catalog_page.search_courses("python")
            assert search_page.is_loaded(), "Страница результатов поиска не загрузилась"

        # 3. ПРИМЕНЕНИЕ ФИЛЬТРА "БЕСПЛАТНО"
        with allure.step("3. Применение фильтра 'Бесплатно'"):
            search_page.apply_free_filter()
            assert "free=true" in page.url, "Фильтр 'Бесплатно' не применился в URL"

        # 4. ОТКРЫТИЕ ПЕРВОГО КУРСА (в новой вкладке)
        with allure.step("4. Открытие первого курса"):
            course_page = search_page.open_first_course()  # Теперь возвращает новую страницу

            # Проверяем URL новой вкладки (формат: /course/ID/promo?search=...)
            course_url = course_page.url
            assert "/course/" in course_url, f"Ожидали URL с /course/, но получили: {course_url}"

            allure.attach(
                body=f"URL курса: {course_url}",
                name="course_url",
                attachment_type=allure.attachment_type.TEXT,
            )

        # 5. ПРОВЕРКА СТРАНИЦЫ КУРСА (в новой вкладке)
        with allure.step("5. Проверка открытия курса"):
            # Проверяем, что мы НЕ на странице поиска
            assert (
                "/catalog/search" not in course_url
            ), f"Оказались на странице поиска вместо курса. URL: {course_url}"

            # Проверка: на странице курса есть заголовок h1
            header = course_page.locator("h1").first
            assert header.is_visible(timeout=10000), "Заголовок курса не отображается"

            header_text = header.inner_text()
            assert len(header_text) > 0, "Заголовок курса пустой"

            allure.attach(
                body=f"Заголовок курса: {header_text}",
                name="course_header",
                attachment_type=allure.attachment_type.TEXT,
            )

            # Закрываем вкладку курса (опционально, для чистоты)
            course_page.close()
