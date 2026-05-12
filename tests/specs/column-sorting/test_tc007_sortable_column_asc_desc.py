"""
TC-007 — Verify that clicking a sortable column header sorts the grid in
          ascending order and then descending order, with a visible indicator.

Steps:
  1. Log in as AP Processor and navigate to main dashboard with multiple records.
  2. Identify a sortable column from the grid (Invoice No.).
  3. Click the column header once — grid sorts ascending; indicator shows ascending.
  4. Click the same column header a second time — grid sorts descending; indicator shows descending.

Expected:
  - After first click  : sort direction is 'ascending'.
  - After second click : sort direction is 'descending'; indicator updates accordingly.
  - No errors occur during either sort operation.
"""

import pytest
from playwright.sync_api import expect

from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from utils.config import BASE_URL, USERNAME, PASSWORD

SORTABLE_COLUMN = "Invoice No."


class TestTC007SortableColumnAscDesc:

    def test_tc007_sortable_column_asc_desc(self, page):

        # --- Step 1: Log in and navigate to the dashboard ---
        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        dashboard = DashboardPage(page)
        dashboard._dismiss_cookie_banner()

        # Confirm the dashboard has records before sorting
        record_count = dashboard.get_grid_record_count()
        if record_count == 0:
            pytest.skip(
                "[TC-007] No records visible in the grid for the current date range. "
                "Adjust the date filter or seed data before running this test."
            )

        # --- Step 2: Confirm Invoice No. is a sortable column ---
        assert dashboard.is_column_header_sortable(SORTABLE_COLUMN), (
            f"[TC-007] Column '{SORTABLE_COLUMN}' does not have the sortable class — "
            "it cannot be used as the test target."
        )

        # --- Step 3: First click — expect ascending sort ---
        dashboard.click_column_header(SORTABLE_COLUMN)
        direction_after_first_click = dashboard.get_sort_direction(SORTABLE_COLUMN)
        assert direction_after_first_click == "ascending", (
            f"[TC-007] Expected sort direction 'ascending' after first click on "
            f"'{SORTABLE_COLUMN}', got '{direction_after_first_click}'."
        )

        # Verify the sort indicator is visible via the columnheader accessible name
        expect(
            page.get_by_role("columnheader", name=f"{SORTABLE_COLUMN} in ascending")
        ).to_be_visible()

        # --- Step 4: Second click — expect descending sort ---
        dashboard.click_column_header(SORTABLE_COLUMN)
        direction_after_second_click = dashboard.get_sort_direction(SORTABLE_COLUMN)
        assert direction_after_second_click == "descending", (
            f"[TC-007] Expected sort direction 'descending' after second click on "
            f"'{SORTABLE_COLUMN}', got '{direction_after_second_click}'."
        )

        # Indicator updated to descending
        expect(
            page.get_by_role("columnheader", name=f"{SORTABLE_COLUMN} in descending")
        ).to_be_visible()
