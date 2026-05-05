import os
from datetime import datetime
from playwright.sync_api import Page
from utils.config import SCREENSHOTS_DIR


class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def navigate(self, url: str):
        self.page.goto(url, wait_until="networkidle", timeout=60000)

    def is_text_visible(self, text: str) -> bool:
        return self.page.get_by_text(text, exact=False).first.is_visible()

    def take_screenshot(self, name: str) -> str:
        os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(SCREENSHOTS_DIR, f"{name}_{timestamp}.png")
        self.page.screenshot(path=path, full_page=True)
        print(f"Screenshot saved: {path}")
        return path
