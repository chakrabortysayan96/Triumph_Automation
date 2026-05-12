import warnings
from playwright.sync_api import Page, Locator
from pages.invoice_details_page import InvoiceDetailsPage
from locators.invoice_due_date_locators import InvoiceDueDateLocators


class InvoiceDueDatePage(InvoiceDetailsPage):
    """Page Object for Invoice Due Date functionality on the AP Invoice Management dashboard."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.edit_button: Locator = page.get_by_role("button", name="Edit").first
        self.save_button: Locator = page.get_by_role("button", name="Save").first
        self.cancel_button: Locator = page.get_by_role("button", name="Cancel").first
        self.history_tab: Locator = page.get_by_role("tab", name="History").first
        self.due_date_column_header: Locator = page.locator("th", has_text="Invoice Due Date").first
        self.invoice_no_cells: Locator = page.locator(InvoiceDueDateLocators.INVOICE_NO_CELL_CSS)

    # ─── Cookie banner ────────────────────────────────────────────────────────

    def dismiss_cookie_banner(self) -> None:
        """Remove the OneTrust consent overlay so the grid is fully interactive."""
        self.page.evaluate(
            f"document.getElementById('{InvoiceDueDateLocators.COOKIE_BANNER_ID}')?.remove()"
        )

    # ─── Dashboard navigation ─────────────────────────────────────────────────

    def _wait_for_spinner_gone(self, appear_timeout: int = 3_000, gone_timeout: int = 30_000) -> None:
        """Wait for the MUI loading spinner to disappear after a grid reload."""
        spinner = self.page.locator(InvoiceDueDateLocators.LOADING_SPINNER_CSS)
        try:
            spinner.wait_for(state="visible", timeout=appear_timeout)
        except Exception:
            pass  # spinner may have appeared and disappeared before we caught it
        spinner.wait_for(state="hidden", timeout=gone_timeout)

    def navigate_to_invoice(self, invoice_number: str) -> None:
        """Search for invoice_number on the dashboard and open its details page."""
        search = self.page.get_by_test_id(InvoiceDueDateLocators.SEARCH_INPUT_TESTID)
        search.fill(invoice_number)
        search.press("Enter")
        self._wait_for_spinner_gone()
        # Dismiss the OneTrust cookie banner via JS so it cannot intercept clicks.
        self.page.evaluate(
            "() => { const el = document.getElementById('onetrust-consent-sdk'); if (el) el.remove(); }"
        )
        # Click the invoice-number link in the matching row
        self.invoice_no_cells.filter(
            has=self.page.get_by_text(invoice_number, exact=True)
        ).locator("button").first.click(timeout=10_000)
        self.page.wait_for_url("**/invoice**", timeout=30_000)
        self.page.wait_for_load_state("networkidle", timeout=30_000)
        # Wait for the invoice heading (h3) to confirm React has rendered the shell.
        self.page.wait_for_selector("h3", state="visible", timeout=20_000)
        # CRITICAL: networkidle and h3 both fire before the invoice data API call
        # returns — the page renders a shell with em-dash placeholders first.
        # Poll the DOM until at least one p[for] field shows a real (non-dash) value,
        # confirming the API response has been painted by React.
        self.page.wait_for_function(
            """() => {
                const DASHES = new Set(['\u2014', '\u2013', '\u2012', '\u2010', '-']);
                const labels = document.querySelectorAll('p[for]');
                for (const lbl of labels) {
                    const wrapper = lbl.parentElement && lbl.parentElement.parentElement;
                    const valEl = wrapper && wrapper.children[1] &&
                        (wrapper.children[1].querySelector('p[class*="truncate"]') ||
                         wrapper.children[1].querySelector('p'));
                    if (valEl) {
                        const t = (valEl.innerText || '').trim();
                        if (t && !DASHES.has(t)) return true;
                    }
                }
                return false;
            }""",
            timeout=30_000,
        )

    def get_dashboard_due_date(self, invoice_number: str) -> str:
        """
        Search for invoice_number on the dashboard and return the Invoice Due Date
        column value for the matching row.  Returns an empty string if the cell
        is not found or the column is hidden.

        Network-mutating: triggers a filtered grid request.
        """
        search = self.page.get_by_test_id(InvoiceDueDateLocators.SEARCH_INPUT_TESTID)
        search.fill(invoice_number)
        search.press("Enter")
        self._wait_for_spinner_gone()
        row = self.page.locator(InvoiceDueDateLocators.DASHBOARD_ROW_CSS).filter(
            has=self.page.locator(InvoiceDueDateLocators.INVOICE_NO_CELL_CSS).filter(
                has_text=invoice_number
            )
        ).first
        due_date_cell = row.locator(InvoiceDueDateLocators.INVOICE_DUE_DATE_CELL_CSS)
        try:
            due_date_cell.wait_for(state="visible", timeout=10_000)
            return due_date_cell.inner_text().strip()
        except Exception:
            warnings.warn(
                f"[InvoiceDueDatePage] get_dashboard_due_date: "
                f"Invoice Due Date cell not visible for invoice '{invoice_number}'. "
                "Check that the 'Invoice Due Date' column is active in the dashboard view."
            )
            return ""

    def navigate_back_to_dashboard(self) -> None:
        """Click Back and wait for the dashboard URL to load."""
        self.back_button.click()
        self.page.wait_for_url("**/dashboard**", timeout=30_000)
        self.page.wait_for_load_state("networkidle", timeout=30_000)

    # ─── Details page — read fields ──────────────────────────────────────────

    def _get_field_value(self, field_for: str, timeout: int = 8_000) -> str:
        """
        Read a view-mode field value by its label's `for` attribute.

        DOM structure (confirmed via live inspection):
          p[for="fieldFor"]         ← label paragraph
            └─ div.inline.align-middle
                 └─ div.RUPldswjkpaxnk7J5NsV   ← wrapper with 2 children
                      child[0] = label div
                      child[1] = value div  →  p.truncate  ← value text

        Uses JavaScript evaluation (confirmed working) rather than XPath
        because Playwright's locator XPath engine silently fails on custom
        `for` attributes on non-label elements in this app.

        Returns "" when the label is not found, or the value is blank / dash.
        """
        DASHES = {"\u2014", "\u2013", "\u2012", "-", "\u2014", "\u2013"}
        try:
            # state="visible" ensures the label has been painted by React,
            # eliminating the read-before-render race condition.
            # 20s timeout because the invoice detail page can take >8s on cold load.
            self.page.wait_for_selector(
                f'p[for="{field_for}"]', state="visible", timeout=20_000
            )
            result: str = self.page.evaluate(
                """(fieldFor) => {
                    const label = document.querySelector('p[for="' + fieldFor + '"]');
                    if (!label) return '';
                    const wrapper = label.parentElement && label.parentElement.parentElement;
                    const valueEl = wrapper && wrapper.children[1] &&
                        (wrapper.children[1].querySelector('p[class*="truncate"]') ||
                         wrapper.children[1].querySelector('p'));
                    return valueEl ? (valueEl.innerText || '').trim() : '';
                }""",
                field_for,
            )
            if not result or result in DASHES:
                return ""
            return result
        except Exception:
            return ""

    def is_save_button_enabled(self) -> bool:
        return self.save_button.is_enabled()

    def get_invoice_due_date(self) -> str:
        """Return the Invoice Due Date display value (view mode); "" when blank."""
        return self._get_field_value(InvoiceDueDateLocators.INVOICE_DUE_DATE_FOR)

    def get_invoice_receipt_date(self) -> str:
        """Return the Invoice Receipt Date display value (view mode)."""
        return self._get_field_value(InvoiceDueDateLocators.INVOICE_RECEIPT_DATE_FOR)

    def get_bu_country(self) -> str:
        """
        Return the BU Country field value from the invoice details page (view mode).

        Uses p[for='countryCode'] — confirmed via live DOM inspection:
          _get_field_value('countryCode') returns 'DK' for invoice 380-0063-00-01.

        Returns "" when the field is absent, blank, or a dash.
        """
        return self._get_field_value(InvoiceDueDateLocators.BU_COUNTRY_FOR)

    # ─── Details page — edit actions ─────────────────────────────────────────

    def click_edit(self) -> None:
        self.edit_button.click()

    def click_save(self) -> None:
        """Click Save and wait for the page to fully settle (networkidle)."""
        self.save_button.click()
        self.page.wait_for_load_state("networkidle", timeout=30_000)

    def save_and_reload(self) -> None:
        """
        Save the invoice and force a full page reload so the Due Date field
        reflects the backend-recomputed value.

        The backend computes the new due date asynchronously; 'networkidle' fires
        before the updated value is pushed back into the DOM, so a reload is
        required to guarantee a fresh read.
        """
        self.click_save()
        self.page.reload()
        self.page.wait_for_load_state("networkidle", timeout=30_000)
        self.page.wait_for_selector("h3", state="visible", timeout=20_000)

    def save_and_reload_if_changed(self) -> None:
        """
        Save if there are pending changes, then reload.

        When no change has been made (Save is disabled) — e.g., when the
        receipt date already equals the target value — exits edit mode by
        clicking Cancel before reloading.  This avoids a Playwright error
        from clicking a disabled Save button.
        """
        if self.is_save_button_enabled():
            self.click_save()
        else:
            self.cancel_button.click()
            self.page.wait_for_load_state("networkidle", timeout=15_000)
        self.page.reload()
        self.page.wait_for_load_state("networkidle", timeout=30_000)
        self.page.wait_for_selector("h3", state="visible", timeout=20_000)

    def update_invoice_receipt_date(self, date_value: str) -> None:
        """Fill the Invoice Receipt Date input in edit mode."""
        # Playwright fill() selects all existing text and replaces it
        self.page.locator(InvoiceDueDateLocators.INVOICE_RECEIPT_DATE_INPUT).fill(date_value)

    def update_invoice_date(self, date_value: str) -> None:
        """Fill the Invoice Date input in edit mode."""
        self.page.locator(InvoiceDueDateLocators.INVOICE_DATE_INPUT).fill(date_value)

    def update_payment_terms(self, payment_terms: str) -> None:
        """
        Set Payment Terms via the MUI Autocomplete widget.

        The actual option texts include a pipe separator, e.g.:
          "0013 | within 90 days without cash discount"
          "BE01 | Immediate"

        Strategy:
          1. Click to focus the input (required to open the MUI Autocomplete).
          2. Fill with a short search term (the numeric/alpha code before the pipe)
             to trigger the dropdown and filter options.
          3. Click the first option whose text contains the search term.

        The `payment_terms` argument is used as-is for the fill and option match.
        Callers should pass a value that uniquely identifies one option (e.g. "0013",
        "BE01", "Immediate").
        """
        pt_input = self.page.locator(InvoiceDueDateLocators.PAYMENT_TERMS_INPUT)
        # Click first to ensure the MUI Autocomplete is focused and ready
        pt_input.click(timeout=5_000)
        pt_input.fill(payment_terms)
        # Wait for the autocomplete listbox to appear and click the first match
        option = self.page.get_by_role("option").filter(has_text=payment_terms).first
        option.wait_for(state="visible", timeout=10_000)
        option.click()

    # ─── Details page — tabs ──────────────────────────────────────────────────

    def click_history_tab(self) -> None:
        self.history_tab.click()

    def sort_due_date_column(self) -> None:
        self.due_date_column_header.click()
