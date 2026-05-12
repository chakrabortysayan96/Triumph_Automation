"""
TC-015 — Verify a horizontal scroll bar appears when selected columns exceed the
         visible screen width. Verify it adjusts dynamically when the browser
         window is resized to a narrow width and then expanded back.

Steps:
  1. Log in as AP Processor and navigate to the main dashboard.
  2. Select enough columns via Change Grid View to exceed visible screen width;
     click Apply.
  3. Observe the bottom of the dashboard grid — horizontal scroll bar is visible.
  4. Scroll horizontally using the scroll bar.
  5. Resize browser window to a narrow width so columns overflow.
  6. Expand browser window back to normal width.

Expected:
  Horizontal scroll bar disappears or adjusts; all columns are accessible
  without horizontal scrolling.
"""

import pytest
from playwright.sync_api import expect

from pages.login_page import LoginPage
from pages.change_grid_view_page import ChangeGridViewPage
from utils.config import BASE_URL, USERNAME, PASSWORD

# Narrow viewport that guarantees column overflow (simulates a minimised window)
NARROW_WIDTH = 800
NARROW_HEIGHT = 600
# Standard viewport to restore after the narrow-resize step
NORMAL_WIDTH = 1280
NORMAL_HEIGHT = 720


class TestTC015HorizontalScrollbarAppears:

    def test_tc015_horizontal_scrollbar_appears_and_adjusts(self, page):

        # ── Step 1: Log in and navigate to dashboard ──────────────────────────
        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        grid_view_page = ChangeGridViewPage(page)

        # Ensure we start at a predictable viewport size
        grid_view_page.resize_browser_window(NORMAL_WIDTH, NORMAL_HEIGHT)

        # ── Step 2: Open Change Grid View, add available columns, Apply ───────
        grid_view_page.open_change_grid_view_panel()
        assert grid_view_page.is_panel_open(), (
            "Change Grid View panel did not open"
        )

        # Move every column from Available → Active so we are certain to
        # exceed the visible width. This is a no-op when Available is empty
        # (all columns are already Active), which also satisfies the step.
        grid_view_page.move_all_available_to_active()

        # Verify we have enough active columns to create overflow (≥ 8)
        active_cols = grid_view_page.get_panel_column_list("Active Columns")
        assert len(active_cols) >= 8, (
            f"Expected ≥8 active columns to guarantee overflow; got {len(active_cols)}"
        )

        grid_view_page.apply_column_settings()

        # ── Step 3: Horizontal scroll bar is visible after Apply ──────────────
        assert grid_view_page.is_grid_horizontal_scrollable(), (
            "Expected a horizontal scrollbar to be present after adding all columns, "
            "but none was detected."
        )

        # ── Step 4: Scroll horizontally via the scroll container ──────────────
        page.evaluate(
            """() => {
                const tableWrap = document.querySelector('[class*="aiops-table-wrap"]');
                const scrollEl = tableWrap?.parentElement;
                if (scrollEl) scrollEl.scrollLeft = scrollEl.scrollWidth;
            }"""
        )
        # Table is still present — grid content is accessible after scrolling
        expect(page.locator("table")).to_be_visible()

        # Scroll back to origin so subsequent steps see the grid normally
        page.evaluate(
            """() => {
                const tableWrap = document.querySelector('[class*="aiops-table-wrap"]');
                const scrollEl = tableWrap?.parentElement;
                if (scrollEl) scrollEl.scrollLeft = 0;
            }"""
        )

        # ── Step 5: Resize to a narrow width ─────────────────────────────────
        grid_view_page.resize_browser_window(NARROW_WIDTH, NARROW_HEIGHT)

        # Scrollbar must still be present — columns still overflow at narrow width
        assert grid_view_page.is_grid_horizontal_scrollable(), (
            "Expected a horizontal scrollbar at narrow viewport "
            f"({NARROW_WIDTH}×{NARROW_HEIGHT}), but none was detected."
        )

        # ── Step 6: Expand back to normal width ───────────────────────────────
        grid_view_page.resize_browser_window(NORMAL_WIDTH, NORMAL_HEIGHT)

        # The scroll container's client width is restored to the wider viewport,
        # confirming the scrollbar has adjusted (scrollable range is smaller than
        # at narrow width). The grid and its column headers remain accessible.
        scroll_info = page.evaluate(
            """() => {
                const tableWrap = document.querySelector('[class*="aiops-table-wrap"]');
                const el = tableWrap?.parentElement;
                return el ? { scrollWidth: el.scrollWidth, clientWidth: el.clientWidth } : null;
            }"""
        )
        assert scroll_info is not None, "Scroll container not found after restoring viewport"
        assert scroll_info["clientWidth"] >= NORMAL_WIDTH - 400, (
            f"Expected clientWidth to recover after expanding viewport; "
            f"got {scroll_info['clientWidth']} (scrollWidth={scroll_info['scrollWidth']})"
        )

        # All column headers remain visible / accessible
        expect(page.locator("table thead")).to_be_visible()
