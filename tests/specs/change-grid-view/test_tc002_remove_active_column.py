"""
TC-002 — Validate Customize Dashboard View by Removing from Active Column

Steps:
  1. Navigate to dashboard with valid credentials; locate Change Grid View button.
  2. Click the Change Grid View icon; verify the popup shows available and active columns
     with Apply/Cancel buttons.
  3. Remove Invoice No., Supplier, Business Unit from Active to Available.
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

COLUMNS_TO_REMOVE = ["Invoice No.", "Supplier", "Business Unit"]


class TestTC002RemoveActiveColumn:

    def test_tc002_customize_dashboard_remove_active_column(self, page):
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

        active_columns = grid_view_page.get_panel_column_list("Active Columns")
        assert len(active_columns) > 0, "Active Columns list is empty"

        for col in COLUMNS_TO_REMOVE:
            if col not in active_columns:
                pytest.skip(
                    f"Prerequisite not met: '{col}' is not in Active Columns. "
                    "A previous test may have already removed it. Re-run after resetting state."
                )

        # --- Step 3: Remove columns from Active to Available ---
        for col in COLUMNS_TO_REMOVE:
            grid_view_page.move_column_to_available(col)

        # --- Step 4: Apply; verify removed columns are gone from the grid ---
        grid_view_page.apply_column_settings()

        for col in COLUMNS_TO_REMOVE:
            assert not grid_view_page.is_column_visible_in_grid(col), \
                f"Column '{col}' is still visible on the dashboard after removal"

        # --- Step 5: Clear cookies, re-login; verify columns remain removed ---
        grid_view_page.clear_cookies_and_relogin(BASE_URL, USERNAME, PASSWORD)

        for col in COLUMNS_TO_REMOVE:
            assert not grid_view_page.is_column_visible_in_grid(col), \
                f"Column '{col}' reappeared on the dashboard after re-login"
