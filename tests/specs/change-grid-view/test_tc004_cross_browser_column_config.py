"""
TC-004 — Validate Customize Dashboard View in Different Browser

Steps (applied to both Chrome and Edge):
  1. Navigate to dashboard with valid credentials.
  2. Click the Change Grid View icon; verify the popup opens with available/active columns.
  3. Move Invoice No., Supplier, BU Country to Available;
     add Invoice Due Date, Payment Terms, Payment Method to Active.
  4. Click Apply; verify rearranged columns appear on the dashboard.
  5. Minimize, Maximize, Zoom-in, Zoom-out browser; verify panel controls are accessible.
  6. Refresh browser; clear cookies; re-login; verify the customized column selection
     is maintained.

Expected: The customized column selection and order should be maintained.

Browser strategy:
  • test_tc004_chrome_…  → uses the default Chromium fixture (headless=False per conftest).
  • test_tc004_edge_…    → launches Microsoft Edge inline; skips gracefully when Edge
                           is not installed on the host machine.
"""

import pytest
import warnings
from playwright.sync_api import expect

from pages.login_page import LoginPage
from pages.change_grid_view_page import ChangeGridViewPage
from utils.config import BASE_URL, USERNAME, PASSWORD

COLUMNS_TO_REMOVE = ["Invoice No.", "Supplier", "BU Country"]
COLUMNS_TO_ADD    = ["Invoice Due Date", "Payment Terms", "Payment Method"]

VIEWPORT_SCENARIOS = [
    ("minimize",  640,  480),
    ("maximize", 1920, 1080),
    ("zoom-in",   800,  600),
    ("zoom-out", 2560, 1440),
]


def _run_column_config_scenario(test_page):
    """
    Core TC-004 logic, browser-agnostic.  Accepts any Playwright Page object.
    """
    # Step 1 — login
    login_page = LoginPage(test_page)
    login_page.navigate(BASE_URL)
    login_page.login(USERNAME, PASSWORD)

    grid_view_page = ChangeGridViewPage(test_page)

    # Step 2 — open panel; verify structure
    grid_view_page.open_change_grid_view_panel()
    assert grid_view_page.is_panel_open(), \
        "Change Grid View panel did not open after clicking the settings icon"
    expect(test_page.get_by_test_id("apply-button")).to_be_visible()
    expect(test_page.get_by_test_id("cancel-button")).to_be_visible()

    # Step 3 — move columns (safe variants handle cross-test state drift)
    for col in COLUMNS_TO_REMOVE:
        grid_view_page.move_column_to_available_safe(col)
    for col in COLUMNS_TO_ADD:
        grid_view_page.move_column_to_active_safe(col)

    # Step 4 — apply; verify added columns are in the grid
    grid_view_page.apply_column_settings()
    for col in COLUMNS_TO_ADD:
        assert grid_view_page.is_column_visible_in_grid(col), \
            f"Column '{col}' not visible on dashboard after Apply"

    # Step 5 — reopen panel; resize viewport; verify controls remain accessible
    grid_view_page.open_change_grid_view_panel()
    for label, width, height in VIEWPORT_SCENARIOS:
        grid_view_page.resize_browser_window(width, height)
        expect(test_page.get_by_test_id("apply-button")).to_be_visible(timeout=5000), \
            f"Apply button not visible after {label} resize ({width}×{height})"
        expect(test_page.get_by_test_id("cancel-button")).to_be_visible(timeout=5000), \
            f"Cancel button not visible after {label} resize ({width}×{height})"

    grid_view_page.resize_browser_window(1280, 720)
    grid_view_page.cancel_column_settings()

    # Step 6 — clear cookies, re-login; verify persistence
    grid_view_page.clear_cookies_and_relogin(BASE_URL, USERNAME, PASSWORD)
    for col in COLUMNS_TO_ADD:
        assert grid_view_page.is_column_visible_in_grid(col), \
            f"Column '{col}' not maintained after re-login"


class TestTC004CrossBrowserColumnConfig:

    def test_tc004_chrome_cross_browser_column_config(self, page):
        """TC-004 (Chrome / Chromium) — standard pytest-playwright page fixture."""
        _run_column_config_scenario(page)

    def test_tc004_edge_cross_browser_column_config(self, page, edge_page):
        """
        TC-004 (Microsoft Edge) — uses the `edge_page` fixture from conftest.py
        which creates Edge from the same shared playwright_instance, avoiding
        any nested sync_playwright() / asyncio loop conflicts.
        Skips gracefully when Microsoft Edge is not installed (handled in the fixture).
        """
        _run_column_config_scenario(edge_page)
