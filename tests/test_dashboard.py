import pytest
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from utils.config import BASE_URL, USERNAME, PASSWORD
from locators.dashboard_locators import DashboardLocators


class TestAPInvoiceDashboard:

    def test_ap_invoice_text_visible(self, page):
        # Verifies that the AP Invoice Management heading is visible on the
        # dashboard after a successful login.
        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        dashboard = DashboardPage(page)
        dashboard.take_screenshot("dashboard_loaded")

        elements = dashboard.get_ap_invoice_elements()
        print(f"\nFound {len(elements)} element(s) with 'AP Invoice Management': {elements}")

        assert dashboard.is_ap_invoice_text_visible(), \
            "'AP Invoice Management' text not found on the dashboard page"

    def test_grid_column_swap(self, page):
        # Opens the Change Grid View panel and swaps the two columns defined
        # in DashboardLocators, then verifies the dashboard reflects the change.
        #
        # To target different columns, update only these two fields in
        # locators/dashboard_locators.py — no other file needs to change:
        #   ACTIVE_STATUS_COLUMN          → column moved OUT of the grid
        #   AVAILABLE_INVOICE_TYPE_COLUMN → column moved INTO the grid
        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        dashboard = DashboardPage(page)

        # Open the column settings panel
        dashboard.open_grid_settings()

        # Move the configured Active column out to Available
        dashboard.move_active_column_to_available(DashboardLocators.ACTIVE_STATUS_COLUMN)

        # Move the configured Available column in to Active
        dashboard.move_available_column_to_active(DashboardLocators.AVAILABLE_INVOICE_TYPE_COLUMN)

        # Apply and wait for the grid to reload
        dashboard.apply_column_settings()
        dashboard.take_screenshot("grid_after_column_swap")

        # The column moved into Active must now be visible in the dashboard
        assert dashboard.is_column_header_visible(DashboardLocators.AVAILABLE_INVOICE_TYPE_COLUMN), (
            f"'{DashboardLocators.AVAILABLE_INVOICE_TYPE_COLUMN}' column header not found "
            f"in the dashboard after moving it to Active"
        )

        # The column moved out to Available must no longer be visible in the dashboard
        assert not dashboard.is_column_header_visible(DashboardLocators.ACTIVE_STATUS_COLUMN), (
            f"'{DashboardLocators.ACTIVE_STATUS_COLUMN}' column header is still visible "
            f"in the dashboard after moving it to Available"
        )
