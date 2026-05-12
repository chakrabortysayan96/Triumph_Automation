import os
import pytest
from datetime import datetime
from playwright.sync_api import sync_playwright
from utils.config import VIDEOS_DIR, SCREENSHOTS_DIR, DOWNLOADS_DIR


@pytest.fixture(scope="session")
def playwright_instance():
    # Single sync_playwright() context shared across the whole test session.
    # All browser fixtures (Chromium, Edge) must be created from this instance
    # so there is only one event loop in play.
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser_instance(playwright_instance):
    browser = playwright_instance.chromium.launch(headless=False)
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def edge_browser(playwright_instance):
    # Provides a Microsoft Edge browser for the TC-004 cross-browser test.
    # Skips the test gracefully when Edge is not installed on the host.
    try:
        browser = playwright_instance.chromium.launch(channel="msedge", headless=False)
    except Exception as exc:
        pytest.skip(f"Microsoft Edge is not installed or could not be launched: {exc}")
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def edge_page(edge_browser):
    os.makedirs(VIDEOS_DIR, exist_ok=True)
    ctx = edge_browser.new_context(
        record_video_dir=VIDEOS_DIR,
        record_video_size={"width": 1280, "height": 720},
    )
    pg = ctx.new_page()
    yield pg
    ctx.close()


@pytest.fixture(scope="function")
def context(browser_instance):
    os.makedirs(VIDEOS_DIR, exist_ok=True)
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)
    ctx = browser_instance.new_context(
        record_video_dir=VIDEOS_DIR,
        record_video_size={"width": 1280, "height": 720},
        accept_downloads=True,
    )
    yield ctx
    ctx.close()


@pytest.fixture(scope="function")
def page(context):
    pg = context.new_page()
    yield pg
    pg.close()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture(scope="function", autouse=True)
def screenshot_on_failure(page, request):
    yield
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(SCREENSHOTS_DIR, f"FAIL_{request.node.name}_{timestamp}.png")
        page.screenshot(path=path, full_page=True)
        print(f"\nFailure screenshot saved: {path}")
