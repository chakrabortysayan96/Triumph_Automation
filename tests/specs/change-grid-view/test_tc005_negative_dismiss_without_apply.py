"""
TC-005 — Validate Customize Dashboard View - Negative Cases

Steps:
  1. Navigate to dashboard with valid credentials; locate Change Grid View button.
  2. Click the Change Grid View icon; verify the popup opens with available/active columns
     and all required fields (Apply, Cancel, arrow buttons).
  3. Rearrange columns in the active area; move Po No., Supplier, Business Unit between areas.
  4. Close or dismiss the popup WITHOUT clicking Apply.

Expected: Popup closes; dashboard loads with minimum delay; no changes are applied to
          the dashboard (column state is identical to what it was before the panel was opened).

"""

import pytest
from playwright.sync_api import expect

from pages.login_page import LoginPage
from pages.change_grid_view_page import ChangeGridViewPage
from utils.config import BASE_URL, USERNAME, PASSWORD

COLUMNS_TO_TOGGLE = ["PO No.", "Supplier", "Business Unit"]


class TestTC005NegativeDismissWithoutApply:

    def test_tc005_customize_dashboard_negative_dismiss(self, page):
        # --- Step 1: Navigate to dashboard ---
        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        grid_view_page = ChangeGridViewPage(page)

        # Record pre-test grid column visibility for later comparison
        # (capture which of the target columns are currently visible)
        pre_test_visibility = {
            col: grid_view_page.is_column_visible_in_grid(col)
            for col in COLUMNS_TO_TOGGLE
        }

        # --- Step 2: Open panel; verify required fields ---
        grid_view_page.open_change_grid_view_panel()

        assert grid_view_page.is_panel_open(), \
            "Change Grid View panel did not open"

        expect(page.get_by_test_id("apply-button")).to_be_visible()
        expect(page.get_by_test_id("cancel-button")).to_be_visible()
        expect(page.get_by_test_id("move-right-button")).to_be_attached()
        expect(page.get_by_test_id("move-left-button")).to_be_attached()

        available_columns = grid_view_page.get_panel_column_list("Available Columns")
        active_columns    = grid_view_page.get_panel_column_list("Active Columns")
        assert len(available_columns) > 0, "Available Columns list is empty"
        assert len(active_columns) > 0,    "Active Columns list is empty"

        # --- Step 3: Rearrange without applying ---
        # Move each target column to whichever list it does NOT currently belong to.
        # This simulates the user making changes that will be discarded.
        for col in COLUMNS_TO_TOGGLE:
            if col in active_columns:
                grid_view_page.move_column_to_available_safe(col)
            elif col in available_columns:
                grid_view_page.move_column_to_active_safe(col)

        # Confirm rearranged state is reflected inside the panel (before dismissal)
        assert grid_view_page.is_panel_open(), \
            "Panel closed unexpectedly before Cancel was clicked"

        # --- Step 4: Dismiss without applying ---
        grid_view_page.cancel_column_settings()

        assert not grid_view_page.is_panel_open(), \
            "Panel is still open after clicking Cancel"

        # Verify no changes were persisted on the dashboard
        for col in COLUMNS_TO_TOGGLE:
            post_visibility = grid_view_page.is_column_visible_in_grid(col)
            assert post_visibility == pre_test_visibility[col], (
                f"Column '{col}' visibility changed after Cancel: "
                f"was {pre_test_visibility[col]}, now {post_visibility}"
            )
