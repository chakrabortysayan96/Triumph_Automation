"""
TC-001 — Validate Customize Dashboard View by Adding Available Column to Active Column

Steps:
  1. Navigate to dashboard with valid credentials; locate Change Grid View button.
  2. Click the Change Grid View icon; verify the popup shows available and active columns
     with Apply/Cancel buttons and scrollable lists.
  3. Select Payment Terms, Payment Method, Supplier ID from Available and move to Active.
  4. Click Apply.
  5. Refresh browser; clear cookies; re-login; verify the customized column selection
     and order is maintained.

Expected: The customized column selection and order should be maintained.
"""

import pytest
from playwright.sync_api import expect

from pages.login_page import LoginPage
from pages.change_grid_view_page import ChangeGridViewPage
from utils.config import BASE_URL, USERNAME, PASSWORD

COLUMNS_TO_ADD = ["Payment Terms", "Payment Method", "Supplier ID"]


class TestTC001AddAvailableColumn:

    def test_tc001_customize_dashboard_add_available_column(self, page):
        # --- Step 1: Navigate to dashboard ---
        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        grid_view_page = ChangeGridViewPage(page)

        # --- Step 2: Open panel; verify structure ---
        grid_view_page.open_change_grid_view_panel()

        assert grid_view_page.is_panel_open(), \
            "Change Grid View panel did not open after clicking the settings icon"

        expect(page.get_by_test_id("apply-button")).to_be_visible()
        expect(page.get_by_test_id("cancel-button")).to_be_visible()
        expect(page.get_by_test_id("move-right-button")).to_be_attached()
        expect(page.get_by_test_id("move-left-button")).to_be_attached()

        available_columns = grid_view_page.get_panel_column_list("Available Columns")
        assert len(available_columns) > 0, "Available Columns list is empty"

        active_columns = grid_view_page.get_panel_column_list("Active Columns")
        assert len(active_columns) > 0, "Active Columns list is empty"

        for col in COLUMNS_TO_ADD:
            if col not in available_columns:
                pytest.skip(
                    f"Prerequisite not met: '{col}' is not in Available Columns. "
                    "A previous test may have already added it. Re-run after resetting state."
                )

        # --- Step 3: Move columns to Active ---
        for col in COLUMNS_TO_ADD:
            grid_view_page.move_column_to_active(col)

        # --- Step 4: Apply ---
        grid_view_page.apply_column_settings()

        for col in COLUMNS_TO_ADD:
            assert grid_view_page.is_column_visible_in_grid(col), \
                f"Column '{col}' is not visible on the dashboard after clicking Apply"

        # --- Step 5: Clear cookies, re-login; verify persistence ---
        grid_view_page.clear_cookies_and_relogin(BASE_URL, USERNAME, PASSWORD)

        for col in COLUMNS_TO_ADD:
            assert grid_view_page.is_column_visible_in_grid(col), \
                f"Column '{col}' is not maintained on the dashboard after re-login"
