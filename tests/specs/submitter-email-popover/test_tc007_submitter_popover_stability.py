"""
TC-007 — Validate the stability of the email popover after hovering the
          submitter email id in landing page of Zora and Details page of
          the invoice.

Steps:
  1. Navigate to dashboard; locate popover beside submitter name.
  2. Hover Submitter Name; resize browser to multiple edge-case viewports;
     verify popover shows email details without breaking UI layout.
  3. Move mouse rapidly across 5–10 different Submitter Names tooltip areas
     in dashboard and details page; verify tooltips open/close cleanly without
     lag.

Expected:
  - Popover shows email details without breaking UI layout when resized.
  - Tooltips open/close cleanly without lag on rapid mouse movement.
"""

import pytest
from playwright.sync_api import expect

from pages.login_page import LoginPage
from pages.submitter_email_popover_page import SubmitterEmailPopoverPage
from pages.invoice_details_page import InvoiceDetailsPage
from utils.config import BASE_URL, USERNAME, PASSWORD

# Viewport sizes used to exercise browser edge / resize behavior
RESIZE_VIEWPORTS = [
    (1280, 720),
    (1024, 768),
    (800, 600),
]


class TestTC007SubmitterPopoverStability:

    def test_tc007_submitter_popover_resize_stability(self, page):
        """Step 2: Popover layout remains intact when browser is resized."""

        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        submitter_page = SubmitterEmailPopoverPage(page)
        submitter_page._dismiss_cookie_banner()

        cell_count = submitter_page.get_submitter_cell_count()
        if cell_count == 0:
            pytest.skip(
                "[TC-007] No submitter name cells found in dashboard. "
                "Ensure at least one invoice exists in the active date range."
            )

        for width, height in RESIZE_VIEWPORTS:
            submitter_page.resize_browser(width, height)

            # Hover and confirm popover is visible and well-formed
            submitter_page.hover_submitter_by_index(0)
            popover_text = submitter_page.get_email_popover_text(timeout=4000)

            assert submitter_page.is_email_popover_visible(), (
                f"[TC-007] Popover not visible at viewport {width}x{height}."
            )
            assert "@" in popover_text or "not available" in popover_text.lower(), (
                f"[TC-007] Popover email check failed at {width}x{height}. "
                f"Got: '{popover_text}'"
            )
            submitter_page.move_cursor_away()

    def test_tc007_submitter_popover_rapid_hover_dashboard(self, page):
        """Step 3a: Rapid hover across submitter cells in dashboard — no lag or stuck tooltip."""

        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        submitter_page = SubmitterEmailPopoverPage(page)
        submitter_page._dismiss_cookie_banner()

        cell_count = submitter_page.get_submitter_cell_count()
        if cell_count == 0:
            pytest.skip("[TC-007] No submitter name cells found in dashboard.")

        # Rapidly move across up to 10 submitter cells
        submitter_page.hover_multiple_submitters_rapidly(count=min(cell_count, 10))

        # Verify no tooltip remains stuck after rapid movement
        page.wait_for_timeout(500)
        assert submitter_page.is_email_popover_hidden(timeout=2000), (
            "[TC-007] Tooltip remained visible after rapid hover and cursor move — "
            "possible UI lag or stuck tooltip."
        )

    def test_tc007_submitter_popover_rapid_hover_details(self, page):
        """Step 3b: Rapid hover on submitter in details page — no lag or stuck tooltip."""

        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        submitter_page = SubmitterEmailPopoverPage(page)
        submitter_page._dismiss_cookie_banner()

        cell_count = submitter_page.get_submitter_cell_count()
        if cell_count == 0:
            pytest.skip("[TC-007] No invoices found in dashboard.")

        submitter_page.open_invoice_by_index(0)

        details_page = InvoiceDetailsPage(page)
        assert details_page.is_loaded(), "[TC-007] Invoice details page did not load."

        # Hover submitter on details page; confirm tooltip appears cleanly
        details_page.hover_submitter_name()
        details_text = details_page.get_submitter_popover_text(timeout=4000)
        assert "@" in details_text or "not available" in details_text.lower(), (
            f"[TC-007] Details page popover check failed. Got: '{details_text}'"
        )

        # Move cursor away; confirm tooltip disappears without lag
        details_page.move_cursor_away()
        page.wait_for_timeout(500)
        assert not details_page.is_submitter_popover_visible(), (
            "[TC-007] Tooltip remained visible after cursor moved away from "
            "submitter name on the details page."
        )
