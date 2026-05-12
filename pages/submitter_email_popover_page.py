import warnings

from playwright.sync_api import Page, Locator
from pages.base_page import BasePage
from locators.submitter_email_popover_locators import SubmitterEmailPopoverLocators


class SubmitterEmailPopoverPage(BasePage):
    """Page Object for Submitter Email Popover feature on the dashboard."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.search_input: Locator = page.locator(SubmitterEmailPopoverLocators.SEARCH_INPUT)
        self.submitter_cells: Locator = page.locator(SubmitterEmailPopoverLocators.SUBMITTER_CELL)
        self.email_tooltip: Locator = page.locator(SubmitterEmailPopoverLocators.EMAIL_TOOLTIP)

    def _dismiss_cookie_banner(self) -> None:
        self.page.evaluate(
            "document.getElementById('onetrust-consent-sdk')?.remove()"
        )

    def search_invoice(self, invoice_number: str) -> None:
        self.search_input.clear()
        self.search_input.fill(invoice_number)
        self.page.wait_for_load_state("load", timeout=15000)

    def get_submitter_cell_count(self) -> int:
        return self.submitter_cells.count()

    def hover_submitter_by_index(self, index: int = 0) -> None:
        self.submitter_cells.nth(index).hover()

    def get_email_popover_text(self, timeout: int = 4000) -> str:
        # Priority 1: look for a tooltip containing an email address.
        # Filtering by '@' avoids accidentally capturing tooltips from adjacent
        # cells (e.g. Invoice No. buttons whose MUI tooltip also has a <label>)
        # that can briefly appear as the mouse travels to the submitter column.
        email_tooltip = self.page.locator('[role="tooltip"]').filter(has_text="@").first
        try:
            email_tooltip.wait_for(state="visible", timeout=timeout)
            return email_tooltip.inner_text().strip()
        except Exception:
            pass

        # Priority 2: look for the "Email not available" tooltip.
        not_avail_tooltip = self.page.locator('[role="tooltip"]').filter(
            has_text=SubmitterEmailPopoverLocators.EMAIL_NOT_AVAILABLE_TEXT
        ).first
        try:
            not_avail_tooltip.wait_for(state="visible", timeout=timeout // 2)
            return not_avail_tooltip.inner_text().strip()
        except Exception:
            pass

        return ""

    def is_email_popover_visible(self, timeout: int = 3000) -> bool:
        try:
            email = self.page.locator('[role="tooltip"]').filter(has_text="@").first
            email.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            pass
        try:
            not_avail = self.page.locator('[role="tooltip"]').filter(
                has_text=SubmitterEmailPopoverLocators.EMAIL_NOT_AVAILABLE_TEXT
            ).first
            return not_avail.is_visible()
        except Exception:
            return False

    def is_email_popover_hidden(self, timeout: int = 2000) -> bool:
        # Check that both the email tooltip and the "not available" tooltip are hidden
        try:
            email = self.page.locator('[role="tooltip"]').filter(has_text="@").first
            email.wait_for(state="hidden", timeout=timeout)
            return True
        except Exception:
            return not self.is_email_popover_visible(timeout=500)

    def move_cursor_away(self) -> None:
        self.page.mouse.move(0, 0)

    def open_invoice_by_index(self, index: int = 0) -> None:
        """Click the Invoice No. button in the same <tr> as the submitter cell
        at `index`. This ensures the dashboard row and submitter row stay in sync
        even when the DOM has placeholder rows that shift plain nth() lookups.
        """
        submitter_td = self.submitter_cells.nth(index)
        # Walk up to the parent <tr>, then scope the Invoice No. button to that row.
        row_tr = submitter_td.locator("xpath=..")
        row_tr.locator("td.dashboard-table-invoiceNo button").first.click()
        self.page.wait_for_url(
            SubmitterEmailPopoverLocators.DETAILS_URL_PATTERN, timeout=20000
        )
        self.page.wait_for_load_state("load", timeout=15000)

    def open_invoice_by_number(self, invoice_number: str) -> bool:
        """Search for an invoice, then click it to open the details page.

        Returns True if successfully navigated to the details page,
        False if the invoice was not found in the dashboard.
        Network-mutating: returns bool so callers decide whether to skip.
        """
        self.search_invoice(invoice_number)
        self.page.wait_for_timeout(1000)

        if self.submitter_cells.count() == 0:
            warnings.warn(
                f"[SubmitterEmailPopoverPage] Invoice {invoice_number} not found in dashboard."
            )
            return False

        try:
            first_submitter = self.submitter_cells.first
            row_tr = first_submitter.locator("xpath=..")
            row_tr.locator("td.dashboard-table-invoiceNo button").first.click(timeout=5000)
            self.page.wait_for_url(
                SubmitterEmailPopoverLocators.DETAILS_URL_PATTERN, timeout=20000
            )
            self.page.wait_for_load_state("load", timeout=15000)
            return True
        except Exception:
            warnings.warn(
                f"[SubmitterEmailPopoverPage] Failed to open invoice {invoice_number}."
            )
            return False

    def hover_multiple_submitters_rapidly(self, count: int = 5) -> None:
        total = self.submitter_cells.count()
        for i in range(min(count, total)):
            self.submitter_cells.nth(i).hover()
        self.move_cursor_away()

    def resize_browser(self, width: int, height: int) -> None:
        self.page.set_viewport_size({"width": width, "height": height})
