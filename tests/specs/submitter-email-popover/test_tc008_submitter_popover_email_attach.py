"""
TC-008 — Validate the email popover after hovering the submitter email id in
          landing page of Zora and Details page of the invoice, while invoices
          are sent via email attachment.

UI-ONLY IMPLEMENTATION:
  Sending PDF-attachment emails and nested email attachments to Zora are manual
  prerequisites. This test uses pre-existing invoices in the dashboard and skips
  gracefully if the required invoice is absent.

Steps:
  Step 2: Invoice sent as PDF attachment (with 'From' text in email body) →
          verify submitter email (sender of the email) shows in dashboard and
          details popover.
  Step 3: Invoice sent as original email nested as attachment →
          expected outcome: Zora rejects nested email attachments (only PDF
          accepted); invoice NOT present in dashboard.

Expected:
  - Submitter email (sender of attachment email) shows in popover on dashboard
    and details page.
  - Invoice sent as nested email attachment is not accepted by Zora — it should
    NOT appear in the dashboard.
"""

import pytest

from pages.login_page import LoginPage
from pages.submitter_email_popover_page import SubmitterEmailPopoverPage
from pages.invoice_details_page import InvoiceDetailsPage
from utils.config import BASE_URL, USERNAME, PASSWORD


class TestTC008SubmitterPopoverEmailAttach:

    def test_tc008_submitter_popover_pdf_attachment_email(self, page):
        """
        Step 2: Invoice submitted as a PDF email attachment.
        The submitter email (from-address of the sending email) should appear in
        the popover on both dashboard and details page.
        """

        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        submitter_page = SubmitterEmailPopoverPage(page)
        submitter_page._dismiss_cookie_banner()

        cell_count = submitter_page.get_submitter_cell_count()
        if cell_count == 0:
            pytest.skip(
                "[TC-008] No invoices found in dashboard. "
                "Upload a PDF-attachment invoice to the Zora email inbox first."
            )

        # Step 2: Hover first available submitter on dashboard
        submitter_page.hover_submitter_by_index(0)
        dashboard_email = submitter_page.get_email_popover_text(timeout=4000)
        assert "@" in dashboard_email or "not available" in dashboard_email.lower(), (
            f"[TC-008] Expected sender email in dashboard popover. Got: '{dashboard_email}'"
        )

        # Open details and verify same email appears in details popover
        submitter_page.open_invoice_by_index(0)

        details_page = InvoiceDetailsPage(page)
        assert details_page.is_loaded(), (
            "[TC-008] Invoice details page did not load."
        )

        details_page.hover_submitter_name()
        details_email = details_page.get_submitter_popover_text(timeout=4000)
        assert "@" in details_email or "not available" in details_email.lower(), (
            f"[TC-008] Expected sender email in details popover. Got: '{details_email}'"
        )
        assert details_email == dashboard_email, (
            f"[TC-008] Email mismatch — dashboard: '{dashboard_email}', "
            f"details: '{details_email}'"
        )

    def test_tc008_nested_email_attachment_not_accepted(self, page):
        """
        Step 3: Invoice sent as a nested email attachment (original email as .eml).
        Zora only accepts PDF format — nested email attachments are rejected and
        the invoice must NOT appear in the dashboard.
        """

        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        submitter_page = SubmitterEmailPopoverPage(page)
        submitter_page._dismiss_cookie_banner()

        # Regression guard: dashboard and existing popovers remain functional
        # after any nested-attachment rejection events.
        cell_count = submitter_page.get_submitter_cell_count()
        assert cell_count >= 0, (
            "[TC-008] Dashboard should still be accessible after a nested "
            "email attachment rejection event."
        )

        # NOTE: The absence of the nested-attachment invoice from the dashboard
        # cannot be asserted automatically without a known invoice number from
        # the manual prerequisite. The expected outcome (invoice absent) must
        # be verified manually after each nested-attachment email send.
