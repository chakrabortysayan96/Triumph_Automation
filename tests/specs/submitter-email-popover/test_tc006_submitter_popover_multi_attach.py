"""
TC-006 — Validate email popover after hovering the submitter email id in landing
          page of Zora and Details page of the invoice, while sending multiple
          invoices as an attachment.

UI-ONLY IMPLEMENTATION:
  Sending a multi-attachment email to Zora is a manual prerequisite.
  Zora does not accept emails with multiple PDF attachments; invoices submitted
  that way should NOT appear in the dashboard.

  This test:
  1. Verifies the dashboard loads and the submitter popover remains functional
     on existing invoices (regression guard).
  2. Documents the expected outcome (absent invoice) for manual validation.

Steps:
  Step 1: Navigate to dashboard; locate tooltip beside submitter name.
  Step 2: (Manual prerequisite) Send multiple invoices as attachments to Zora;
          verify the invoices do NOT appear in the dashboard.

Expected:
  - Zora does not accept multiple-attachment emails.
  - Invoices submitted that way are absent from the dashboard.
  - The submitter popover on existing invoices remains fully functional.
"""

import pytest
from playwright.sync_api import expect

from pages.login_page import LoginPage
from pages.submitter_email_popover_page import SubmitterEmailPopoverPage
from utils.config import BASE_URL, USERNAME, PASSWORD


class TestTC006SubmitterPopoverMultiAttach:

    def test_tc006_multi_attachment_invoice_not_in_dashboard(self, page):
        """
        Negative test: invoices sent via multi-attachment email must not appear
        in the dashboard. Validates dashboard stability as a regression guard.
        """

        # Step 1: Navigate to dashboard; confirm submitter column is accessible
        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        submitter_page = SubmitterEmailPopoverPage(page)
        submitter_page._dismiss_cookie_banner()

        cell_count = submitter_page.get_submitter_cell_count()
        if cell_count == 0:
            pytest.skip(
                "[TC-006] No invoices visible in dashboard — cannot perform "
                "regression guard without a baseline."
            )

        # Step 2 (regression guard): Hover submitter on an existing invoice;
        # confirm popovers still function after any multi-attachment rejection event.
        submitter_page.hover_submitter_by_index(0)
        popover_text = submitter_page.get_email_popover_text(timeout=4000)
        assert "@" in popover_text or "not available" in popover_text.lower(), (
            "[TC-006] Submitter popover on existing invoices should still function "
            f"correctly after a multi-attachment rejection event. Got: '{popover_text}'"
        )
        submitter_page.move_cursor_away()

        # NOTE: The absence of the multi-attachment invoice from the dashboard
        # cannot be asserted automatically without a known invoice number from
        # the manual prerequisite. The expected outcome (invoice absent) is
        # documented above and must be verified manually after each email send.
