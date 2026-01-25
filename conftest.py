import pytest
import structlog
import os
import allure
from allure_commons.types import AttachmentType
from allure_commons._allure import StepContext
from typing import Generator
from dotenv import load_dotenv
from playwright.sync_api import Page, Browser, Playwright, sync_playwright, BrowserContext

load_dotenv()

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)
logger = structlog.get_logger(__name__)


def pytest_configure(config):
    """Конфигурация Allure для pytest."""
    # Регистрируем метки
    config.addinivalue_line("markers", "ui: UI тесты")
    config.addinivalue_line("markers", "smoke: Smoke тесты")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Собираем информацию о тесте для Allure."""
    outcome = yield
    report = outcome.get_result()

    # Прикрепляем дополнительные данные при падении теста
    if report.when == "call" and report.failed:
        # Получаем page из фикстуры, если есть
        page = item.funcargs.get("page")
        if page:
            # Скриншот при падении
            screenshot = page.screenshot(full_page=True)
            allure.attach(
                screenshot, name="screenshot_on_failure", attachment_type=AttachmentType.PNG
            )


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Конфигурация контекста браузера для всей сессии."""
    return {
        **browser_context_args,
        "ignore_https_errors": True,
    }


@pytest.fixture(scope="session")
def playwright_instance() -> Generator[Playwright, None, None]:
    """Фикстура для управления жизненным циклом Playwright"""
    logger.info("Запуск Playwright")
    with sync_playwright() as playwright:
        yield playwright


@pytest.fixture(scope="session")
def browser(playwright_instance: Playwright) -> Generator[Browser, None, None]:
    """Запуск браузера один раз на всю сессию тестов"""
    logger.info("Запуск браузера Chromium")
    browser = playwright_instance.chromium.launch()
    yield browser
    logger.info("Закрытые браузера")
    browser.close()


@pytest.fixture
def context(browser: Browser) -> Generator[BrowserContext, None, None]:
    """Контекст браузера (одна сессия)"""
    logger.info("Создание контекста браузера")
    context = browser.new_context()
    yield context
    logger.info("Закрытие контекста")
    context.close()


@pytest.fixture
def page(context) -> Generator[Page, None, None]:
    """Фикстура страницы - одна сессия на все тесты"""
    logger.info("Создание новой страницы")
    page = context.new_page()

    page.set_default_timeout(30000)
    page.set_default_navigation_timeout(30000)

    yield page
    logger.info("Закрытие страницы")


@pytest.fixture
def credentials():
    """Фикстура с тестовыми учетными данными из .env"""
    login = os.getenv("STEPIK_LOGIN")
    password = os.getenv("STEPIK_PASSWORD")

    if not login or not password:
        logger.erroe("Не найдены учетные данные в .env файле")
        raise ValueError("Добавьте STEPIK_LOGIN и STEPIK_PASSWORD в .env файл")
    logger.info("Учетные данные загружены", login=login[:3] + "***")
    return {"login": login, "password": password}


def pytest_sessionfinish(exitstatus):
    """Хук для логгирования завершения тестовой сессии"""
    logger.info("Тестовая сессия заверешена", exitstatus=exitstatus)
