"""
TC-016 — Verify no horizontal scroll bar appears when selected columns fit
         within the visible screen width.

Steps:
  1. Log in as AP Processor and navigate to the main dashboard.
  2. Select only a few columns via Change Grid View that fit within visible
     screen width; click Apply.
  3. Observe the bottom of the dashboard grid.

Expected:
  No horizontal scroll bar is visible; all columns are displayed without
  the need for horizontal scrolling.
"""

import pytest
from playwright.sync_api import expect

from pages.login_page import LoginPage
from pages.change_grid_view_page import ChangeGridViewPage
from utils.config import BASE_URL, USERNAME, PASSWORD

# Columns to keep active — short names that comfortably fit within a 1280 px
# viewport without triggering a horizontal scrollbar.
FEW_COLUMNS = ["System ID", "Invoice No.", "Supplier", "Status"]


class TestTC016NoHorizontalScrollbar:

    def test_tc016_no_horizontal_scrollbar_with_few_columns(self, page):

        # ── Step 1: Log in and navigate to dashboard ──────────────────────────
        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        grid_view_page = ChangeGridViewPage(page)

        # ── Step 2: Open Change Grid View, keep only FEW_COLUMNS, Apply ───────
        grid_view_page.open_change_grid_view_panel()
        assert grid_view_page.is_panel_open(), (
            "Change Grid View panel did not open"
        )

        # Move all active columns except FEW_COLUMNS to Available, then
        # ensure every column in FEW_COLUMNS is in Active (they may already be).
        grid_view_page.clear_active_columns_except(FEW_COLUMNS)

        # After clearing, move any of FEW_COLUMNS that ended up in Available
        # back to Active (handles the case where they were not originally active).
        for col in FEW_COLUMNS:
            available = grid_view_page.get_panel_column_list("Available Columns")
            if col in available:
                grid_view_page.move_column_to_active(col)

        # Confirm the Active list now contains exactly FEW_COLUMNS
        active_after = grid_view_page.get_panel_column_list("Active Columns")
        for col in FEW_COLUMNS:
            assert col in active_after, (
                f"Expected '{col}' to be in Active Columns after setup; "
                f"actual Active list: {active_after}"
            )
        assert len(active_after) == len(FEW_COLUMNS), (
            f"Expected exactly {len(FEW_COLUMNS)} active column(s); "
            f"got {len(active_after)}: {active_after}"
        )

        grid_view_page.apply_column_settings()

        # ── Step 3: No horizontal scroll bar visible ───────────────────────────
        assert not grid_view_page.is_grid_horizontal_scrollable(), (
            f"Expected NO horizontal scrollbar with only {FEW_COLUMNS} active, "
            "but one was detected."
        )

        # All selected columns are displayed (headers visible in the grid)
        for col in FEW_COLUMNS:
            assert grid_view_page.is_column_header_visible(col), (
                f"Column header '{col}' is not visible in the grid after Apply."
            )
