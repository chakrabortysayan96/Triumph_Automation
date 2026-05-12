import warnings
from playwright.sync_api import Page, Locator, expect
from pages.base_page import BasePage
from locators.requester_email_popover_locators import RequesterEmailPopoverLocators as L


class RequesterEmailPopoverPage(BasePage):
    """Page Object for Requester Email Popover feature (dashboard + invoice details)."""

    def __init__(self, page: Page):
        super().__init__(page)
        # Dashboard locators
        self.invoice_rows: Locator = page.locator(L.DASHBOARD_ROW_CSS)
        self.email_tooltip: Locator = page.get_by_role(L.EMAIL_TOOLTIP_ROLE)

    # ── Dashboard helpers ────────────────────────────────────────────────

    def navigate_to_dashboard(self, base_url: str) -> None:
        """Navigate to the AP Invoice Management dashboard and wait for the grid."""
        self.page.goto(base_url, wait_until="networkidle", timeout=60_000)
        # Remove cookie SDK overlay so it cannot intercept pointer events.
        self.page.evaluate(
            "() => { const el = document.getElementById('onetrust-consent-sdk');"
            " if (el) el.remove(); }"
        )
        expect(self.invoice_rows.first).to_be_visible(timeout=30_000)

    def search_invoice(self, invoice_number: str) -> None:
        """Type an invoice number into the search box and press Enter."""
        box = self.page.get_by_test_id(L.SEARCH_BOX_TESTID)
        box.fill(invoice_number)
        box.press("Enter")
        expect(self.invoice_rows.first).to_be_visible(timeout=30_000)

    def get_requester_name_cell(self, row_index: int = 0) -> Locator:
        """Return the Requester name cell (first .dashboard-table-requester) for a given row."""
        return (
            self.invoice_rows.nth(row_index)
            .locator(L.DASHBOARD_REQUESTER_CELL_CSS)
            .first
        )

    def get_submitter_name_cell(self, row_index: int = 0) -> Locator:
        """Return the Submitter name cell for a given row."""
        return (
            self.invoice_rows.nth(row_index)
            .locator(L.DASHBOARD_SUBMITTER_CELL_CSS)
            .first
        )

    def hover_requester_in_dashboard(self, row_index: int = 0) -> None:
        """Hover the Requester name cell in the specified row."""
        self.get_requester_name_cell(row_index).hover(timeout=15_000)

    def hover_submitter_in_dashboard(self, row_index: int = 0) -> None:
        """Hover the Submitter name cell in the specified row."""
        self.get_submitter_name_cell(row_index).hover(timeout=15_000)

    def move_cursor_away(self) -> None:
        """Move the pointer to the page origin to dismiss any active tooltip."""
        self.page.mouse.move(0, 0)

    # ── Tooltip helpers ───────────────────────────────────────────────────

    def get_tooltip_email(self) -> str:
        """Return the visible email text from the active MUI Tooltip."""
        tooltip = self.page.locator(L.EMAIL_TOOLTIP_CSS).first
        return tooltip.inner_text().strip()

    def is_tooltip_visible(self) -> bool:
        """
        True when at least one MUI Tooltip popper is currently visible.
        Waits up to 5 s to allow for MUI enter animation.
        """
        try:
            # wait_for_selector with :visible pseudo is not supported by all engines;
            # use Playwright's built-in visible filter via count check instead.
            self.page.wait_for_function(
                "() => [...document.querySelectorAll('[role=\"tooltip\"]')]"
                ".some(el => el.getBoundingClientRect().width > 0)",
                timeout=5_000,
            )
            return True
        except Exception:
            return False

    def is_tooltip_hidden(self) -> bool:
        """
        True when NO MUI Tooltip popper has visible dimensions.
        MUI uses opacity transitions (not display:none), so we check
        getBoundingClientRect().width rather than Playwright's is_visible().
        Waits up to 5 s for the exit animation to complete.
        """
        try:
            self.page.wait_for_function(
                "() => ![...document.querySelectorAll('[role=\"tooltip\"]')]"
                ".some(el => el.getBoundingClientRect().width > 0)",
                timeout=5_000,
            )
            return True
        except Exception:
            return False

    # ── Details page helpers ─────────────────────────────────────────────

    def open_invoice_by_id(self, system_id: str) -> None:
        """Click the System ID button to open the invoice details page."""
        self.page.get_by_role("button", name=system_id).first.click()
        self.page.wait_for_load_state("networkidle", timeout=30_000)

    def hover_requester_in_details(self) -> None:
        """Hover the Requester value field on the invoice details page."""
        value = self.page.locator(f"xpath={L.DETAILS_REQUESTER_VALUE_XPATH}").first
        value.hover(timeout=15_000)

    def hover_submitter_in_details(self) -> None:
        """Hover the Submitter value field on the invoice details page."""
        value = self.page.locator(f"xpath={L.DETAILS_SUBMITTER_VALUE_XPATH}").first
        value.hover(timeout=15_000)

    def get_requester_name_in_details(self) -> str:
        """Return the visible requester name text on the details page (no hover)."""
        return (
            self.page.locator(f"xpath={L.DETAILS_REQUESTER_VALUE_XPATH}")
            .first
            .inner_text()
            .strip()
        )

    # ── Stability helpers ─────────────────────────────────────────────────

    def resize_browser(self, width: int, height: int) -> None:
        """Resize the browser viewport."""
        self.page.set_viewport_size({"width": width, "height": height})

    def hover_multiple_requesters_rapidly(self, max_rows: int = 5) -> None:
        """
        Hover across up to *max_rows* Requester name cells quickly to test
        rapid tooltip open/close behaviour.  Stops early if fewer rows exist.
        """
        count = min(self.invoice_rows.count(), max_rows)
        for i in range(count):
            self.get_requester_name_cell(i).hover(timeout=10_000)

    # ── Notes tab helpers ─────────────────────────────────────────────────

    def post_note(self, text: str) -> bool:
        """
        Post a comment on the Notes tab.  Returns True when the Post button
        becomes enabled and was clicked; False if it remains disabled (network
        error or insufficient permission).
        """
        self.page.get_by_role("tab", name=L.NOTES_TAB_NAME).click()
        box = self.page.get_by_role(L.NOTES_TEXTBOX_ROLE).first
        box.fill(text)
        post_btn = self.page.get_by_role("button", name=L.NOTES_POST_BUTTON_NAME)
        try:
            expect(post_btn).to_be_enabled(timeout=5_000)
            post_btn.click()
            self.page.wait_for_load_state("networkidle", timeout=15_000)
            return True
        except Exception as exc:
            warnings.warn(f"[RequesterEmailPopoverPage.post_note] Post button not enabled: {exc}")
            return False
