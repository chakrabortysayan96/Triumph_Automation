from playwright.sync_api import Page
from pages.base_page import BasePage
from locators.login_locators import LoginLocators


class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

    def click_azure_sso(self):
        # Clicks the Azure SSO button on the app login screen and waits for
        # the Microsoft sign-in page to fully load.
        self.page.get_by_text(LoginLocators.AZURE_SSO_TEXT, exact=False).first.click()
        self.page.wait_for_load_state("networkidle", timeout=30000)

    def enter_email(self, username: str):
        # Fills in the email field and advances to the password step.
        self.page.get_by_placeholder(LoginLocators.EMAIL_PLACEHOLDER).fill(username)
        self.page.get_by_role("button", name=LoginLocators.NEXT_BUTTON_NAME).click()
        self.page.wait_for_load_state("networkidle", timeout=15000)

    def enter_password(self, password: str):
        # Fills in the password and submits the Microsoft sign-in form.
        self.page.get_by_placeholder(LoginLocators.PASSWORD_PLACEHOLDER).fill(password)
        self.page.get_by_role("button", name=LoginLocators.SIGN_IN_BUTTON_NAME).click()
        self.page.wait_for_load_state("networkidle", timeout=15000)

    def handle_stay_signed_in(self):
        # Handles the optional "Stay signed in?" dialog that Microsoft may show.
        # Silently skips if the prompt does not appear.
        try:
            btn = self.page.get_by_role("button", name=LoginLocators.STAY_SIGNED_IN_BUTTON_NAME)
            if btn.is_visible(timeout=5000):
                btn.click()
        except Exception:
            pass

    def login(self, username: str, password: str):
        # Orchestrates the full Azure SSO login flow and waits until the browser
        # has navigated into the application.
        self.click_azure_sso()
        self.enter_email(username)
        self.enter_password(password)
        self.handle_stay_signed_in()
        self.page.wait_for_url(LoginLocators.POST_LOGIN_URL_PATTERN, timeout=120000)
        self.page.wait_for_load_state("networkidle", timeout=30000)
