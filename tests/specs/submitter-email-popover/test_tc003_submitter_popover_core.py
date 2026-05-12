"""
TC-003 — Validate email popover after hovering the submitter name in landing
          page of Zora and Details page of the invoice.

Steps:
  1. Navigate to dashboard; locate submitter name label for each invoice.
  2. Hover on Submitter Name in dashboard table; verify popover appears with
     correct email.
  3. Click invoice to open details page; hover Submitter Name field; verify
     popover email matches dashboard.
  4. View Submitter Name without hovering in details page; return to dashboard
     without hovering; verify only name visible (no inline email).
  5. Hover submitter name again in dashboard and details; move cursor away;
     verify popover disappears immediately.

Expected:
  - Popover appears with correct email on hover in dashboard.
  - Popover email matches details page email.
  - Only submitter name visible without hover.
  - Popover disappears immediately when cursor moves away.
"""

import pytest
from playwright.sync_api import expect

from pages.login_page import LoginPage
from pages.submitter_email_popover_page import SubmitterEmailPopoverPage
from pages.invoice_details_page import InvoiceDetailsPage
from utils.config import BASE_URL, USERNAME, PASSWORD


class TestTC003SubmitterPopoverCore:

    def test_tc003_submitter_popover_core(self, page):

        # --- Step 1: Navigate to dashboard; confirm submitter cells are present ---
        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        submitter_page = SubmitterEmailPopoverPage(page)
        submitter_page._dismiss_cookie_banner()

        cell_count = submitter_page.get_submitter_cell_count()
        if cell_count == 0:
            pytest.skip(
                "[TC-003] No submitter name cells found in the dashboard. "
                "Ensure at least one invoice exists in the active date range."
            )

        # --- Step 2: Hover submitter in dashboard; verify email popover appears ---
        submitter_page.hover_submitter_by_index(0)
        dashboard_email = submitter_page.get_email_popover_text(timeout=4000)

        assert submitter_page.is_email_popover_visible(), (
            "[TC-003] Email popover should be visible while hovering submitter name "
            "in the dashboard."
        )
        assert "@" in dashboard_email or "not available" in dashboard_email.lower(), (
            f"[TC-003] Expected an email address or 'Email not available' in popover, "
            f"got: '{dashboard_email}'"
        )

        # --- Step 3: Open invoice details; hover submitter; verify email matches ---
        submitter_page.open_invoice_by_index(0)

        details_page = InvoiceDetailsPage(page)
        assert details_page.is_loaded(), (
            "[TC-003] Invoice details page did not load after clicking invoice number."
        )

        details_page.hover_submitter_name()
        details_email = details_page.get_submitter_popover_text(timeout=4000)

        assert "@" in details_email or "not available" in details_email.lower(), (
            f"[TC-003] Details page popover email unexpected: '{details_email}'"
        )
        assert details_email == dashboard_email, (
            f"[TC-003] Dashboard email '{dashboard_email}' does not match "
            f"details page email '{details_email}'."
        )

        # --- Step 4: Move cursor away on details; confirm popover gone ---
        details_page.move_cursor_away()
        page.wait_for_timeout(500)
        assert not details_page.is_submitter_popover_visible(), (
            "[TC-003] Popover should not be visible after cursor moves away on "
            "the details page."
        )

        # Navigate back without hovering; confirm no inline email in cell
        details_page.navigate_back()
        submitter_page._dismiss_cookie_banner()
        expect(
            page.locator("td.dashboard-table-submitter").first
        ).not_to_contain_text("@")

        # --- Step 5: Hover again in dashboard; move cursor away; verify disappears ---
        submitter_page.hover_submitter_by_index(0)
        assert submitter_page.is_email_popover_visible(), (
            "[TC-003] Popover should reappear on second hover in dashboard."
        )

        submitter_page.move_cursor_away()
        assert submitter_page.is_email_popover_hidden(timeout=3000), (
            "[TC-003] Popover should disappear immediately when cursor moves "
            "away from the submitter cell."
        )
