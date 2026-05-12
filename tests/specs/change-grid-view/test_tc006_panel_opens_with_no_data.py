"""
TC-006 — Verify Change Grid View Panel Opens When the Dashboard Grid Has No Data Records

Steps:
  1. Log in as AP Processor; navigate to the main dashboard where no invoice records are present.
  2. Click the 'Change Grid View' button.

Expected: The customization panel opens successfully, listing all available columns
          regardless of data state; columns can be selected or deselected.

Data precondition: Dashboard must show 0 invoice records.
  Strategy: apply a date-range filter with a 2-day window far in the future to produce 0 results.
  If records are still present after filtering, the test is skipped with a clear message.

Assumption: The currently logged-in user has the AP Processor role.
"""

import pytest
from playwright.sync_api import expect

from pages.login_page import LoginPage
from pages.change_grid_view_page import ChangeGridViewPage
from utils.config import BASE_URL, USERNAME, PASSWORD

# A date range that should produce 0 invoice records (far future dates)
FUTURE_START_DATE = "01/01/2099"
FUTURE_END_DATE   = "01/02/2099"


def _set_date_filter(page, start: str, end: str) -> None:
    """Fill the dashboard date-range inputs and wait for the grid to refresh."""
    date_inputs = page.locator('input[placeholder="MM/DD/YYYY"]')
    date_inputs.nth(0).click(click_count=3)
    date_inputs.nth(0).fill(start)
    date_inputs.nth(1).click(click_count=3)
    date_inputs.nth(1).fill(end)
    page.keyboard.press("Enter")
    page.wait_for_load_state("networkidle", timeout=30000)


class TestTC006PanelOpensWithNoData:

    def test_tc006_change_grid_view_panel_opens_with_no_data(self, page):
        # --- Step 1: Login and navigate to dashboard ---
        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        grid_view_page = ChangeGridViewPage(page)

        # Remove the cookie banner before any grid interaction
        grid_view_page._dismiss_cookie_banner()

        # Attempt to reach 0 records by filtering with a far-future date range
        record_count = grid_view_page.get_grid_record_count()
        if record_count > 0:
            _set_date_filter(page, FUTURE_START_DATE, FUTURE_END_DATE)
            record_count = grid_view_page.get_grid_record_count()

        if record_count > 0:
            pytest.skip(
                f"Precondition not met: dashboard still shows {record_count} record(s) "
                "after applying a future date filter. Verify the environment has an "
                "empty invoice state or adjust FUTURE_START_DATE / FUTURE_END_DATE."
            )

        # Confirm the grid is empty
        assert grid_view_page.get_grid_record_count() == 0, \
            "Dashboard still contains records — empty-grid precondition not satisfied"

        # --- Step 2: Click Change Grid View and verify panel opens ---
        grid_view_page.open_change_grid_view_panel()

        assert grid_view_page.is_panel_open(), \
            "Change Grid View panel did not open when the grid has 0 records"

        # Panel must list all available columns (at least 1 in each list)
        available_columns = grid_view_page.get_panel_column_list("Available Columns")
        active_columns    = grid_view_page.get_panel_column_list("Active Columns")

        assert len(available_columns) > 0, \
            "Available Columns list is empty when the grid has no data"
        assert len(active_columns) > 0, \
            "Active Columns list is empty when the grid has no data"

        # Columns can be interacted with (move-right/left buttons are present)
        expect(page.get_by_test_id("move-right-button")).to_be_attached()
        expect(page.get_by_test_id("move-left-button")).to_be_attached()
        expect(page.get_by_test_id("apply-button")).to_be_visible()
        expect(page.get_by_test_id("cancel-button")).to_be_visible()

        # Dismiss without making changes
        grid_view_page.cancel_column_settings()
