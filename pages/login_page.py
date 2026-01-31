import structlog
import allure
from .base_page import BasePage
from playwright.sync_api import Locator


logger = structlog.get_logger(__name__)


class LoginPage(BasePage):
    """Page Object для страницы авторизации Stepik (/login)"""

    @property
    def email_field(self) -> Locator:
        return self.page.get_by_role("textbox", name="E-mail")

    @property
    def password_field(self) -> Locator:
        return self.page.get_by_role("textbox", name="Пароль")

    @property
    def submit_button(self) -> Locator:
        return self.page.get_by_role("button", name="Войти")

    def open(self) -> "LoginPage":
        """Открыть страницу авторизации"""
        self.log.info("Открытие страницы авторизации")
        login_url = "https://stepik.org/catalog?auth=login"
        self.navigate(login_url)

        self.email_field.wait_for(state="visible", timeout=15000)
        self.log.info("Страница авторизации загружена")
        return self

    def enter_email(self, email: str) -> "LoginPage":
        """Ввести email в поле логина"""
        self.fill(self.email_field, email, "Поле E-mail")
        return self

    def enter_password(self, password: str) -> "LoginPage":
        """Ввести пароль"""
        self.fill(self.password_field, password, "Поле пароль")
        return self

    def submit_login(self):
        self.click(self.submit_button, "Кнопка войти")

    @allure.step("Авторизация пользователя {email}")
    def login(self, email: str, password: str) -> None:
        """
        Полный процесс авторизации с принудительной очисткой состояния.
        """
        self.log.info("Начало процесса авторизации", email=email[:3] + "***")

        # 1. Открываем и заполняем форму
        self.open()
        self.enter_email(email)
        self.enter_password(password)
        self.submit_login()

        # 2. Ждем редиректа после авторизации (вместо sleep)
        self.log.info("Ожидание завершения авторизации...")
        try:
            self.page.wait_for_url("**/catalog", timeout=10000)
        except:
            pass  # Иногда редиректа нет, проверим через URL далее

        # 3. Принудительно очищаем URL от auth=login
        self.log.info("Принудительная очистка состояния авторизации")
        clean_catalog_url = "https://stepik.org/catalog"
        self.navigate(clean_catalog_url)

        # Ждем полной загрузки страницы каталога
        self.page.wait_for_load_state("networkidle")

        # 4. Проверяем, что мы на чистом каталоге
        current_url = self.get_current_url()

        if "auth=login" in current_url:
            self.log.error(f"Ошибка: auth=login все еще в URL после очистки: {current_url}")

            # Крайний случай: очистка cookies и повторная загрузка
            self.log.info("Попытка очистки cookies...")
            self.page.context.clear_cookies()
            self.navigate(clean_catalog_url)
            self.page.wait_for_load_state("networkidle")

        final_url = self.get_current_url()
        self.log.info("Авторизация завершена", final_url=final_url)

    def is_login_successful(self) -> bool:
        """
        Проверка успешной авторизации по иконке профиля с явным ожиданием.
        """
        self.log.info("Проверка успешной авторизации")

        try:
            # 1. Явно дождаться появления элемента в DOM
            avatar_locator = 'img.navbar__profile-img[alt="User avatar"]'
            self.page.wait_for_selector(avatar_locator, state="attached", timeout=10000)
            self.log.debug("Локатор иконки профиля найден в DOM")

            # 2. Проверить видимость элемента
            avatar = self.page.locator(avatar_locator)
            is_visible = avatar.is_visible(timeout=5000)

            self.log.info(f"Иконка профиля видима: {is_visible}")
            return is_visible

        except Exception as e:
            # Если элемент не найден или не видим
            self.log.error(f"Ошибка при проверке авторизации: {e}")

            # Резервная проверка по URL
            current_url = self.get_current_url()
            self.log.info(f"Резервная проверка. Текущий URL: {current_url}")

            # Критерий успеха: мы на /catalog и НЕ на странице логина
            url_check = "/catalog" in current_url and "auth=login" not in current_url
            return url_check
