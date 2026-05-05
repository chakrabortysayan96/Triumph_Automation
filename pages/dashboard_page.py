from playwright.sync_api import Page
from pages.base_page import BasePage
from locators.dashboard_locators import DashboardLocators


class DashboardPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

    def get_page_title(self) -> str:
        # Returns the browser tab title of the currently loaded dashboard page.
        return self.page.title()

    def is_ap_invoice_text_visible(self) -> bool:
        # Checks whether the AP Invoice Management heading is visible on the page.
        return self.is_text_visible(DashboardLocators.AP_INVOICE_TEXT)

    def get_ap_invoice_elements(self) -> list:
        # Returns the inner text of every element that matches the
        # AP Invoice Management label (useful for asserting count or content).
        locator = self.page.get_by_text(DashboardLocators.AP_INVOICE_TEXT, exact=False)
        return [locator.nth(i).inner_text() for i in range(locator.count())]

    # -------------------------------------------------------------------------
    # Cookie Banner
    # The OneTrust SDK injects a full-page overlay that blocks all pointer
    # events until dismissed. Removing it via JS is the most reliable approach.
    # -------------------------------------------------------------------------

    def _dismiss_cookie_banner(self):
        self.page.evaluate(
            f"document.getElementById('{DashboardLocators.COOKIE_SDK_ID}')?.remove()"
        )
        self.page.wait_for_timeout(300)

    # -------------------------------------------------------------------------
    # Grid View / Column Settings
    # Methods to open the Change Grid View panel, move columns between the
    # Available and Active lists, and apply the configuration.
    # -------------------------------------------------------------------------

    def open_grid_settings(self):
        # Dismisses the cookie overlay then clicks the column config button
        # (top-right of the grid toolbar). Waits until the panel heading is
        # visible before returning so callers can interact immediately.
        self._dismiss_cookie_banner()
        self.page.locator(
            f'[data-testid="{DashboardLocators.CHANGE_GRID_VIEW_BUTTON_TESTID}"]'
        ).click()
        self.page.get_by_text(DashboardLocators.COLUMN_SETTINGS_HEADING, exact=False).wait_for(
            state="visible", timeout=15000
        )

    def _get_column_section(self, label: str):
        # Returns the parent container of the list identified by `label`
        # ("Available Columns" or "Active Columns"), scoping all item lookups
        # so we never match a column name in the wrong list.
        return self.page.locator("label").filter(has_text=label).locator("..")

    def move_active_column_to_available(self, column_name: str):
        # Selects the column from the Active list then clicks the left-arrow
        # button to move it into the Available list.
        section = self._get_column_section(DashboardLocators.ACTIVE_COLUMNS_LABEL)
        section.get_by_role("button", name=column_name, exact=True).click()
        self.page.locator(
            f'[data-testid="{DashboardLocators.MOVE_TO_AVAILABLE_BUTTON_TESTID}"]'
        ).click()

    def move_available_column_to_active(self, column_name: str):
        # Selects the column from the Available list then clicks the right-arrow
        # button to move it into the Active list.
        section = self._get_column_section(DashboardLocators.AVAILABLE_COLUMNS_LABEL)
        section.get_by_role("button", name=column_name, exact=True).click()
        self.page.locator(
            f'[data-testid="{DashboardLocators.MOVE_TO_ACTIVE_BUTTON_TESTID}"]'
        ).click()

    def apply_column_settings(self):
        # Clicks Apply to confirm the column configuration and waits for the
        # dashboard grid to finish reloading.
        self.page.get_by_role("button", name=DashboardLocators.APPLY_BUTTON).click()
        self.page.wait_for_load_state("networkidle", timeout=30000)

    # -------------------------------------------------------------------------
    # Column Header Verification
    # Checks presence or absence of a column header in the dashboard grid
    # after column settings have been applied.
    # -------------------------------------------------------------------------

    def is_column_header_visible(self, column_name: str) -> bool:
        # Searches for a column header button matching `column_name` inside
        # the grid. Returns True if at least one matching header is found.
        return (
            self.page.locator(f".{DashboardLocators.COLUMN_HEADER_CLASS}")
            .filter(has_text=column_name)
            .count() > 0
        )
