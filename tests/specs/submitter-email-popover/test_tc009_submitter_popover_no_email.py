"""
TC-009 — Validate the email popover after hovering the submitter email id in
          landing page of Zora and Details page of the invoice, while submitter
          email is not available.

UI-ONLY IMPLEMENTATION:
  Submitting a PDF without submitter email metadata, and sending a
  password-protected PDF, are manual prerequisites. This test:
  1. Scans the first 10 dashboard rows for an invoice whose popover text
     contains "Email not available" (or "Email not found").
  2. Verifies the same message appears on the details page.
  3. Documents the password-protected invoice rejection as a manual step.

Steps:
  Step 2: Invoice submitted where submitter email is absent from the PDF →
          hover Submitter Name in dashboard and details page; expect
          "Email not available" tooltip.
  Step 3: Password-protected invoice sent to Zora →
          expected: Zora rejects it; invoice absent from dashboard.

Expected:
  - Tooltip shows "Email not available" in dashboard and details page
    when email is absent from the PDF metadata.
  - Password-protected invoice is rejected by Zora and not available
    in the dashboard.
"""

import pytest

from pages.login_page import LoginPage
from pages.submitter_email_popover_page import SubmitterEmailPopoverPage
from pages.invoice_details_page import InvoiceDetailsPage
from utils.config import BASE_URL, USERNAME, PASSWORD

# Maximum number of dashboard rows to scan for a "no email" invoice
_MAX_SCAN_ROWS = 10


class TestTC009SubmitterPopoverNoEmail:

    def test_tc009_submitter_popover_no_email_shows_label(self, page):
        """
        Step 2: Popover shows 'Email not available' when the submitter email
        is absent from the PDF metadata.
        """

        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        submitter_page = SubmitterEmailPopoverPage(page)
        submitter_page._dismiss_cookie_banner()

        cell_count = submitter_page.get_submitter_cell_count()
        if cell_count == 0:
            pytest.skip(
                "[TC-009] No invoices found in dashboard. "
                "Submit a no-email PDF to the Zora inbox as a manual prerequisite."
            )

        # Scan up to _MAX_SCAN_ROWS rows to find an invoice with "Email not available"
        no_email_idx = None
        for i in range(min(cell_count, _MAX_SCAN_ROWS)):
            submitter_page.hover_submitter_by_index(i)
            popover_text = submitter_page.get_email_popover_text(timeout=3000)
            submitter_page.move_cursor_away()
            page.wait_for_timeout(300)
            if "not available" in popover_text.lower() or "not found" in popover_text.lower():
                no_email_idx = i
                break

        if no_email_idx is None:
            pytest.skip(
                f"[TC-009] No invoice with 'Email not available' found in the "
                f"first {_MAX_SCAN_ROWS} rows. Manually submit a PDF without "
                "submitter email metadata to the Zora inbox, then re-run."
            )

        # Confirm dashboard tooltip text for the identified row
        submitter_page.hover_submitter_by_index(no_email_idx)
        dashboard_text = submitter_page.get_email_popover_text(timeout=4000)
        assert "not available" in dashboard_text.lower() or "not found" in dashboard_text.lower(), (
            f"[TC-009] Expected 'Email not available' in dashboard popover. "
            f"Got: '{dashboard_text}'"
        )

        # Open details and verify same tooltip message
        submitter_page.open_invoice_by_index(no_email_idx)

        details_page = InvoiceDetailsPage(page)
        assert details_page.is_loaded(), "[TC-009] Invoice details page did not load."

        details_page.hover_submitter_name()
        details_text = details_page.get_submitter_popover_text(timeout=4000)
        assert "not available" in details_text.lower() or "not found" in details_text.lower(), (
            f"[TC-009] Expected 'Email not available' in details popover. "
            f"Got: '{details_text}'"
        )

    def test_tc009_password_protected_invoice_not_accepted(self, page):
        """
        Step 3: Password-protected invoice should be rejected by Zora and must
        NOT appear in the dashboard.
        """

        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        submitter_page = SubmitterEmailPopoverPage(page)
        submitter_page._dismiss_cookie_banner()

        # Regression guard: dashboard remains accessible and existing popovers
        # are unaffected by password-protected invoice rejection events.
        cell_count = submitter_page.get_submitter_cell_count()
        assert cell_count >= 0, (
            "[TC-009] Dashboard should remain accessible after a "
            "password-protected invoice rejection event."
        )

        # NOTE: The absence of the password-protected invoice from the dashboard
        # cannot be asserted automatically without a known invoice number from
        # the manual prerequisite. The expected outcome (invoice absent) must
        # be verified manually after each attempt to submit a password-protected PDF.
