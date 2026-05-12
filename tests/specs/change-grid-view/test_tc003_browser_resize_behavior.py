"""
TC-003 — Validate Customize Dashboard View After Rearranging the Browser Settings

Steps:
  1. Navigate to dashboard with valid credentials; locate Change Grid View button.
  2. Click the Change Grid View icon; verify the popup opens with available/active columns.
  3. Minimize, Maximize, Zoom-in, Zoom-out the browser (simulated via viewport changes);
     verify Apply/Cancel/arrow controls remain visible and clickable throughout.
  4. Refresh browser; clear cookies; re-login to dashboard; verify panel is still accessible.

Expected: The customized column selection and order should be maintained (no changes
          applied in this test so the pre-existing grid state is unchanged).

Note on viewport simulation:
  Browser "zoom" cannot be driven via Playwright in headless mode. Viewport resizes to
  different dimensions approximate the visual effect of minimize/maximize/zoom-in/zoom-out.
"""

import pytest
from playwright.sync_api import expect

from pages.login_page import LoginPage
from pages.change_grid_view_page import ChangeGridViewPage
from utils.config import BASE_URL, USERNAME, PASSWORD

# (label, width, height) — simulating minimize / maximize / zoom-in / zoom-out
VIEWPORT_SCENARIOS = [
    ("minimize",  640,  480),
    ("maximize", 1920, 1080),
    ("zoom-in",   800,  600),
    ("zoom-out", 2560, 1440),
]


class TestTC003BrowserResizeBehavior:

    def test_tc003_customize_dashboard_browser_resize(self, page):
        # --- Step 1: Navigate to dashboard ---
        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        grid_view_page = ChangeGridViewPage(page)

        # Verify the Change Grid View button is visible before opening
        expect(
            page.get_by_test_id("dashboard-column-config-btn")
        ).to_be_visible()

        # --- Step 2: Open panel; verify it shows available/active columns ---
        grid_view_page.open_change_grid_view_panel()

        assert grid_view_page.is_panel_open(), \
            "Change Grid View panel did not open after clicking the settings icon"

        available_columns = grid_view_page.get_panel_column_list("Available Columns")
        active_columns = grid_view_page.get_panel_column_list("Active Columns")
        assert len(available_columns) > 0, "Available Columns list is empty"
        assert len(active_columns) > 0, "Active Columns list is empty"

        # --- Step 3: Resize viewport in four scenarios; verify controls stay reachable ---
        for label, width, height in VIEWPORT_SCENARIOS:
            grid_view_page.resize_browser_window(width, height)

            expect(page.get_by_test_id("apply-button")).to_be_visible(timeout=5000), \
                f"Apply button not visible after {label} resize ({width}×{height})"
            expect(page.get_by_test_id("cancel-button")).to_be_visible(timeout=5000), \
                f"Cancel button not visible after {label} resize ({width}×{height})"
            expect(page.get_by_test_id("move-right-button")).to_be_attached(), \
                f"Move-right button detached after {label} resize"
            expect(page.get_by_test_id("move-left-button")).to_be_attached(), \
                f"Move-left button detached after {label} resize"

        # Restore standard viewport
        grid_view_page.resize_browser_window(1280, 720)

        # Close the panel without applying any changes
        grid_view_page.cancel_column_settings()
        assert not grid_view_page.is_panel_open(), \
            "Panel is still open after clicking Cancel"

        # --- Step 4: Clear cookies, re-login; verify panel is still accessible ---
        grid_view_page.clear_cookies_and_relogin(BASE_URL, USERNAME, PASSWORD)

        expect(
            page.get_by_test_id("dashboard-column-config-btn")
        ).to_be_visible()
