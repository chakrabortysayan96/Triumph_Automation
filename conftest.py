import os
import pytest
from datetime import datetime
from playwright.sync_api import sync_playwright
from utils.config import VIDEOS_DIR, SCREENSHOTS_DIR


@pytest.fixture(scope="session")
def browser_instance():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()


@pytest.fixture(scope="function")
def context(browser_instance):
    os.makedirs(VIDEOS_DIR, exist_ok=True)
    ctx = browser_instance.new_context(
        record_video_dir=VIDEOS_DIR,
        record_video_size={"width": 1280, "height": 720},
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
