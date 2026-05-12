import pytest
from pages.login_page import LoginPage
from pages.bypass_approval_page import BypassApprovalPage
from utils.config import BASE_URL, USERNAME, PASSWORD


class TestBypassApprovalFlow:

    def test_aiop_121675_bypass_approval_valid_datapoint(self, page):
        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        bypass_page = BypassApprovalPage(page)

        # TODO: Step 1 — Navigate to dashboard; verify bypass approval flag is visible and all labels on landing page are visible
        # TODO: Step 2 — Click bypass approval flag; click on invoice to see details page; verify flag colour changes and all fields in details page are available (Valid Invoice with all fields)
        # TODO: Step 3 — Navigate back to dashboard; try clicking multiple bypass approval buttons; verify previously selected bypass approval button is still active and multiple flags can be clicked
        # TODO: Step 4 — Navigate back to details page; click Approve button (Valid Invoice with all fields); verify Approve button is clickable and invoice moves to next downstream / is available in ERP
        # TODO: Step 5 — Navigate to landing page; click bypass approval flag for a different invoice; open details; verify approve button available; reload page on details tab and on landing page; verify bypass flag persists after reload and approve button remains clickable

    def test_aiop_122380_bypass_approval_negative_cases(self, page):
        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        bypass_page = BypassApprovalPage(page)

        # TODO: Step 1 — Open application with valid credentials; click bypass approval flag on landing page; open invoice with wrong/incomplete/null/zero data (Incomplete Invoice or invoice with wrong type of data); verify Approve button remains hidden or not clickable as mandatory fields are missing
        # TODO: Step 2 — Click History tab; verify bypass approval activation or deactivation details are shown in the history
        # TODO: Step 3 — Navigate back to landing page; locate invoices with "Posted" or "Discard" status; try to click Bypass Approval flag (Invoice Number: 1543463); verify flag is clickable but Approve button is not clickable for invoices with bypass approval enabled at those statuses
