"""
TC-001 — Validate Invoice Urgent Flag & Approve Invoice Flow With Valid Datapoint

Steps:
  1. Navigate to dashboard; verify bypass approval flag is visible.
  2. Click bypass approval flag on the first row; open invoice details;
     verify flag toggled via History tab; verify all key tabs are present.
  3. Navigate back to dashboard; click a second bypass approval flag;
     verify multiple flags can be toggled independently.
  4. Navigate back to details page; verify Approve button is visible;
     click it if enabled (skip gracefully if mandatory fields are missing).
  5. Navigate to landing page; click bypass flag for a second invoice;
     reload the details page; verify bypass flag history persists after reload.

Expected:
  - Bypass flag is visible and clickable on the dashboard.
  - Toggling the flag records "Urgent bypass approval flag enabled." in History.
  - Multiple bypass flags can be clicked independently.
  - Approve button is visible on the details page (may be disabled for some invoices).
  - Bypass flag history entry persists after a full page reload.
"""

import pytest
from playwright.sync_api import expect

from pages.login_page import LoginPage
from pages.bypass_approval_page import BypassApprovalPage
from utils.config import BASE_URL, USERNAME, PASSWORD


class TestTC001BypassApprovalValidFlow:

    def test_tc001_bypass_approval_valid_datapoint(self, page):

        # ------------------------------------------------------------------
        # Step 1: Navigate to dashboard; verify bypass flags are visible
        # ------------------------------------------------------------------
        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        bypass_page = BypassApprovalPage(page)
        bypass_page.dismiss_cookie_banner()

        expect(
            page.get_by_role("heading", name="AP Invoice Management")
        ).to_be_visible(timeout=15_000)

        # Wait for the async data fetch to populate the grid before reading cells.
        bypass_page.wait_for_grid_loaded()

        flag_count = bypass_page.get_bypass_flag_count()
        assert flag_count > 0, (
            "Expected at least one bypass approval flag in the invoice grid, "
            f"but found {flag_count}."
        )

        # ------------------------------------------------------------------
        # Step 2: Click bypass flag on row 0; open details; verify history
        # ------------------------------------------------------------------
        # Step A: Capture the invoice number and its UUID-based detail URL
        # BEFORE touching the bypass flag.  The URL is the only stable unique
        # identifier for the invoice (invoice numbers can be duplicated).
        invoice_number_row0 = bypass_page.get_invoice_number_in_row(row_index=0)
        invoice_url_row0 = bypass_page.get_invoice_url_for_row(row_index=0)

        # Step B: Click the bypass flag and wait for networkidle so the
        # backend XHR (which writes the History entry) completes BEFORE
        # we navigate to the details page.
        bypass_page.click_bypass_flag(row_index=0)

        # Step C: Navigate directly to the invoice by its UUID so we are
        # guaranteed to land on the same invoice regardless of grid re-sort.
        bypass_page.navigate_to_invoice_url(invoice_url_row0)

        # Verify the details page heading is present
        expect(
            page.locator("h3").filter(has_text="Invoice No.")
        ).to_be_visible(timeout=10_000)

        # Verify core tabs are accessible
        for tab_name in ("Details", "History", "Notes"):
            expect(page.get_by_role("tab", name=tab_name)).to_be_visible(
                timeout=5_000
            )

        # Confirm bypass flag activation was recorded in the History tab.
        # Use expect() with a retry timeout rather than a one-shot text check
        # to tolerate any residual server-side write latency.
        bypass_page.navigate_to_history_tab()
        expect(
            page.get_by_text("Urgent bypass approval flag", exact=False).first
        ).to_be_visible(timeout=15_000)

        # ------------------------------------------------------------------
        # Step 3: Navigate back; click a second bypass flag (multi-flag test)
        # ------------------------------------------------------------------
        bypass_page.navigate_back_to_dashboard()
        bypass_page.dismiss_cookie_banner()
        bypass_page.wait_for_grid_loaded()

        total_flags = bypass_page.get_bypass_flag_count()
        assert total_flags >= 2, (
            f"Expected ≥2 bypass flags for the multi-flag test, found {total_flags}. "
            "Verify the dashboard has at least two invoice rows visible."
        )

        # Click the second row's flag to verify independent toggle
        bypass_page.click_bypass_flag(row_index=1)
        assert bypass_page.get_bypass_flag_count() >= 2, (
            "Bypass flags disappeared from the grid after clicking a second flag."
        )

        # ------------------------------------------------------------------
        # Step 4: Re-open row-0 details; verify Approve button visibility/state
        # ------------------------------------------------------------------
        bypass_page.navigate_back_to_dashboard()
        bypass_page.dismiss_cookie_banner()
        bypass_page.navigate_to_invoice_url(invoice_url_row0)

        assert bypass_page.is_approve_button_visible(), (
            "Approve button is not visible on the invoice details page. "
            f"Invoice: {invoice_number_row0}"
        )

        if not bypass_page.is_approve_button_enabled():
            pytest.skip(
                f"[TC-001] Approve button is disabled for invoice '{invoice_number_row0}'. "
                "Mandatory fields may be incomplete — approval step skipped. "
                "Re-run with a fully populated invoice to validate the approval flow."
            )

        clicked = bypass_page.click_approve_button()
        assert clicked, (
            f"Clicking the Approve button failed for invoice '{invoice_number_row0}'."
        )

        # ------------------------------------------------------------------
        # Step 5: Back to dashboard; click bypass flag for a different invoice;
        #         reload details page; verify bypass history persists
        # ------------------------------------------------------------------
        bypass_page.navigate_back_to_dashboard()
        bypass_page.dismiss_cookie_banner()
        bypass_page.wait_for_grid_loaded()

        # Use row 1 (a different invoice from Step 2).
        # Capture its UUID before touching anything, then click bypass,
        # then navigate directly to it by UUID.
        second_invoice_number = bypass_page.get_invoice_number_in_row(row_index=1)
        invoice_url_row1 = bypass_page.get_invoice_url_for_row(row_index=1)
        bypass_page.click_bypass_flag(row_index=1)
        bypass_page.navigate_to_invoice_url(invoice_url_row1)
        bypass_page.navigate_to_history_tab()

        pre_reload_history = bypass_page.get_history_panel_text()
        assert "Urgent bypass approval flag" in pre_reload_history, (
            f"Bypass flag history not found for invoice '{second_invoice_number}' "
            "before reload."
        )

        # Reload and verify persistence
        bypass_page.reload_page()
        bypass_page.navigate_to_history_tab()
        post_reload_history = bypass_page.get_history_panel_text()

        assert "Urgent bypass approval flag" in post_reload_history, (
            f"Bypass flag history for invoice '{second_invoice_number}' was lost "
            "after a full page reload. Expected the History tab to still contain "
            "the bypass flag event."
        )
