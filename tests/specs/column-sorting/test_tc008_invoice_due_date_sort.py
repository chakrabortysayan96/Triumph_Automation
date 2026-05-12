"""
TC-008 — Verify that the Invoice Due Date column supports ascending and
          descending sort with a visible indicator.

Steps:
  1. Log in as AP Processor and navigate to main dashboard with records.
  2. Ensure Invoice Due Date column is visible in the grid (it is active by default).
  3. Click the Invoice Due Date column header once — grid sorts ascending;
     indicator updates to ascending.
  4. Click the Invoice Due Date column header again — grid sorts descending;
     indicator updates to descending.

Expected:
  - After first click  : sort direction is 'ascending'; rows are date-ordered ascending.
  - After second click : sort direction is 'descending'; indicator updates accordingly.
  - No errors occur.
"""

import pytest
from playwright.sync_api import expect

from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from utils.config import BASE_URL, USERNAME, PASSWORD

SORT_COLUMN = "Invoice Due Date"


class TestTC008InvoiceDueDateSort:

    def test_tc008_invoice_due_date_sort(self, page):

        # --- Step 1: Log in and navigate to the dashboard ---
        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        dashboard = DashboardPage(page)
        dashboard._dismiss_cookie_banner()

        record_count = dashboard.get_grid_record_count()
        if record_count == 0:
            pytest.skip(
                "[TC-008] No records visible in the grid for the current date range. "
                "Adjust the date filter or seed data before running this test."
            )

        # --- Step 2: Ensure Invoice Due Date column is visible ---
        if not dashboard.is_column_header_sortable(SORT_COLUMN):
            pytest.skip(
                f"[TC-008] '{SORT_COLUMN}' is not active in the grid. "
                "Add it via Change Grid View and re-run."
            )

        # --- Step 3: First click — expect ascending sort ---
        dashboard.click_column_header(SORT_COLUMN)
        direction_after_first_click = dashboard.get_sort_direction(SORT_COLUMN)
        assert direction_after_first_click == "ascending", (
            f"[TC-008] Expected sort direction 'ascending' after first click on "
            f"'{SORT_COLUMN}', got '{direction_after_first_click}'."
        )

        # Verify the sort indicator is visible via the columnheader accessible name
        expect(
            page.get_by_role("columnheader", name=f"{SORT_COLUMN} in ascending")
        ).to_be_visible()

        # Verify the grid rows are sorted in ascending date order
        date_values_asc = dashboard.get_column_values(SORT_COLUMN)
        non_empty_asc = [d for d in date_values_asc if d and d != "—"]
        if len(non_empty_asc) >= 2:
            assert non_empty_asc == sorted(non_empty_asc), (
                f"[TC-008] Invoice Due Date values are not in ascending order after first click. "
                f"Got: {non_empty_asc[:5]}"
            )

        # --- Step 4: Second click — expect descending sort ---
        dashboard.click_column_header(SORT_COLUMN)
        direction_after_second_click = dashboard.get_sort_direction(SORT_COLUMN)
        assert direction_after_second_click == "descending", (
            f"[TC-008] Expected sort direction 'descending' after second click on "
            f"'{SORT_COLUMN}', got '{direction_after_second_click}'."
        )

        # Indicator updated to descending
        expect(
            page.get_by_role("columnheader", name=f"{SORT_COLUMN} in descending")
        ).to_be_visible()

        # Verify rows are now in descending date order
        date_values_desc = dashboard.get_column_values(SORT_COLUMN)
        non_empty_desc = [d for d in date_values_desc if d and d != "—"]
        if len(non_empty_desc) >= 2:
            assert non_empty_desc == sorted(non_empty_desc, reverse=True), (
                f"[TC-008] Invoice Due Date values are not in descending order after second click. "
                f"Got: {non_empty_desc[:5]}"
            )
