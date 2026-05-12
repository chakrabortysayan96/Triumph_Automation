import pytest
from pages.login_page import LoginPage
from pages.submitter_email_popover_page import SubmitterEmailPopoverPage
from utils.config import BASE_URL, USERNAME, PASSWORD


class TestSubmitterEmailPopover:

    def test_aiop_122785_submitter_email_popover_basic(self, page):
        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        submitter_page = SubmitterEmailPopoverPage(page)

        # TODO: Step 1 — Navigate to dashboard; locate submitter name label for each invoice row
        # TODO: Step 2 — Hover on Submitter Name in the dashboard table; verify popover appears with correct email address
        # TODO: Step 3 — Click any invoice to open details page; hover Submitter Name field; verify popover shows same email as dashboard
        # TODO: Step 4 — View Submitter Name field in details page without hovering; verify only name is visible, no email inline
        # TODO: Step 5 — Hover submitter in dashboard and details page again; move cursor away; verify popover disappears immediately

    def test_aiop_122786_submitter_email_popover_cross_browser(self, page):
        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        submitter_page = SubmitterEmailPopoverPage(page)

        # TODO: Step 1 — Navigate to dashboard with valid credentials (run in Chrome and Edge)
        # TODO: Step 2 — Upload one invoice (Invoice number: 1274481); hover on Submitter Name in dashboard; verify popover appears with correct email
        # TODO: Step 3 — Click the invoice to go to details page; hover Submitter Name field; verify popover email matches dashboard popover email
        # TODO: Step 4 — View Submitter Name field without hovering in details page; come back to dashboard without hovering; verify only name visible, no inline email
        # TODO: Step 5 — Hover submitter tooltip in dashboard and details page again; move cursor away; verify popover disappears immediately

    def test_aiop_122787_submitter_email_popover_invoice_via_email(self, page):
        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        submitter_page = SubmitterEmailPopoverPage(page)

        # TODO: Step 1 — Navigate to dashboard; locate the tooltip beside submitter name for each invoice
        # TODO: Step 2 — Send one invoice to Zora email box (Invoice number: 250300002106); locate invoice in dashboard; hover Submitter Name; verify sender email appears in popover on dashboard and details page
        # TODO: Step 3 — Forward an email invoice from another person to Zora (Invoice Number: 1100006706); hover Submitter Name; verify original sender email id appears in popover on dashboard and details page
        # TODO: Step 4 — Forward an invoice through multiple persons before sending to Zora; hover Submitter Name; verify latest/last forwarded email id appears in submitter popover on dashboard and details page

    def test_aiop_122788_submitter_email_popover_multiple_attachments_negative(self, page):
        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        submitter_page = SubmitterEmailPopoverPage(page)

        # TODO: Step 1 — Navigate to dashboard; locate tooltip beside submitter name for each invoice
        # TODO: Step 2 — Send multiple invoices as attachments to Zora email box (mix of invoices with and without submitter email in PDF); verify Zora does not accept multiple-attachment email; invoices should not appear in dashboard

    def test_aiop_122789_submitter_email_popover_stability(self, page):
        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        submitter_page = SubmitterEmailPopoverPage(page)

        # TODO: Step 1 — Navigate to dashboard; locate popover beside submitter name for each invoice
        # TODO: Step 2 — Hover on Submitter Name in the table; resize browser and move popover to browser edges (Invoice with valid Submitter Email); verify popover shows email details without breaking UI layout
        # TODO: Step 3 — Move mouse rapidly across 5–10 different Submitter Names tooltip areas in both dashboard and details page (multiple invoice records); verify tooltips open/close cleanly without lag

    def test_aiop_122791_submitter_email_popover_email_attachment(self, page):
        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        submitter_page = SubmitterEmailPopoverPage(page)

        # TODO: Step 1 — Navigate to dashboard; locate popover beside submitter name for each invoice
        # TODO: Step 2 — Send an invoice as attachment to Zora email box with "From" text in email body; hover Submitter Name in dashboard and details page; verify popover shows the sender email id
        # TODO: Step 3 — Send an email with original email as an attachment (nested attachment); hover Submitter Name; verify invoice is not accepted by Zora (only PDF format is accepted as attachment)

    def test_aiop_122792_submitter_email_popover_email_not_available(self, page):
        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        submitter_page = SubmitterEmailPopoverPage(page)

        # TODO: Step 1 — Navigate to dashboard; locate tooltip beside submitter name for each invoice
        # TODO: Step 2 — Send an invoice as attachment to Zora email box where submitter email is not in the PDF; hover Submitter Name in dashboard and details page; verify tooltip shows "Email not available"
        # TODO: Step 3 — Send a password-protected invoice to Zora; verify invoice is rejected and does not appear in the dashboard (password-protected invoices are not allowed)
