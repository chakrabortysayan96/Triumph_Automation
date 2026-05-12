import warnings

from playwright.sync_api import Page, Locator

from pages.base_page import BasePage
from locators.bypass_approval_locators import BypassApprovalLocators


class BypassApprovalPage(BasePage):
    """Page Object for the Bypass Approval / Urgent Flag workflow.

    All methods are synchronous (pytest-playwright sync API).
    Network-mutating methods return bool; failures are logged via warnings.warn.
    """

    def __init__(self, page: Page):
        super().__init__(page)
        # Dashboard locators
        self.search_input: Locator = page.get_by_test_id(
            BypassApprovalLocators.SEARCH_INPUT_TESTID
        )
        self.bypass_flag_cells: Locator = page.locator(
            BypassApprovalLocators.BYPASS_CELL_CSS
        )
        self.invoice_no_cells: Locator = page.locator(
            BypassApprovalLocators.INVOICE_NO_CELL_CSS
        )
        # Detail page locators
        self.approve_button: Locator = page.get_by_role(
            "button", name=BypassApprovalLocators.APPROVE_BUTTON_TEXT, exact=True
        )
        self.back_button: Locator = page.get_by_role(
            "button", name=BypassApprovalLocators.BACK_BUTTON_TEXT, exact=True
        )
        self.history_tab: Locator = page.get_by_role(
            "tab", name=BypassApprovalLocators.HISTORY_TAB_TEXT
        )
        self.history_panel: Locator = page.get_by_role("tabpanel")
        # Internal state — set by search_invoice() if an API error was detected
        self._search_api_error: str | None = None

    # -------------------------------------------------------------------------
    # Utility
    # -------------------------------------------------------------------------

    def dismiss_cookie_banner(self) -> None:
        """Remove the OneTrust cookie-consent overlay via JavaScript if present.

        The overlay intercepts all pointer events until it is dismissed; removing
        it via JS is the most reliable approach (mirrors DashboardPage convention).
        """
        self.page.evaluate(
            f"document.getElementById('{BypassApprovalLocators.COOKIE_BANNER_ID}')?.remove()"
        )

    def wait_for_grid_loaded(self, timeout: int = 20_000) -> None:
        """Wait until at least one invoice row is visible in the grid.

        The AP Invoice Management heading may appear before the async data
        fetch completes.  Callers must use this method before reading any
        grid cell (invoice number, bypass flag, etc.) to avoid timeout errors.
        """
        self.invoice_no_cells.first.wait_for(state="visible", timeout=timeout)

    # -------------------------------------------------------------------------
    # Dashboard — search & grid interaction
    # -------------------------------------------------------------------------

    def search_invoice(self, invoice_number: str) -> None:
        """Fill the search box with *invoice_number* and submit.

        After submitting, waits for the MUI CircularProgress spinner to appear
        (confirming the API call started) and then disappear (confirming it
        completed). This avoids false-positive matches on stale grid data.
        If an API error alert is detected it is captured in self._search_api_error
        before the auto-dismissing MUI Alert disappears.
        """
        self._search_api_error = None

        # Focus the input and clear any existing value
        self.search_input.click()
        self.search_input.fill(invoice_number)

        # Submit the search via Enter
        self.search_input.press("Enter")

        # Wait for the loading spinner to appear (API call started)
        try:
            self.page.wait_for_selector(
                ".MuiCircularProgress-root", state="visible", timeout=5_000
            )
        except Exception:
            pass  # Results may have loaded before spinner was detected

        # Wait for the loading spinner to disappear (API call completed)
        try:
            self.page.wait_for_selector(
                ".MuiCircularProgress-root", state="hidden", timeout=30_000
            )
        except Exception:
            pass  # Fall through if spinner never appeared or results arrived

        # Brief pause for React to commit final DOM state
        self.page.wait_for_timeout(300)

        # Immediately capture any visible error alert text before it auto-dismisses
        try:
            alert_locator = self.page.locator('[role="alert"]').first
            if alert_locator.is_visible(timeout=500):
                self._search_api_error = alert_locator.inner_text(timeout=500).strip()
        except Exception:
            pass

    def is_api_error_visible(self) -> bool:
        """Return True if an API error was detected during the last search_invoice call.

        Uses the cached error text captured immediately after the search, before
        the auto-dismissing MUI Alert disappears from the DOM.
        Also falls back to a live DOM check for the [role=alert] element.
        """
        if self._search_api_error and "Error" in self._search_api_error:
            return True
        # Live fallback
        try:
            alert = self.page.locator('[role="alert"]').filter(
                has_text="Error fetching invoices"
            ).first
            return alert.is_visible(timeout=1_000)
        except Exception:
            return False

    def get_search_api_error(self) -> str | None:
        """Return the last API error message captured during search_invoice(), or None."""
        return self._search_api_error

    def is_no_results_visible(self) -> bool:
        """Return True if the 'No results found' state is currently displayed.

        Waits for the page to settle into either a results state (table rows
        present) or a no-results state before returning, avoiding false negatives
        caused by React rendering delays after network idle.
        """
        try:
            # Wait for the grid to show rows OR the no-results placeholder.
            self.page.wait_for_selector(
                f"td.dashboard-table-invoiceNo, "
                f"text={BypassApprovalLocators.NO_RESULTS_TEXT}",
                timeout=8_000,
            )
        except Exception:
            pass  # Fall through to the visibility check below.
        try:
            return self.page.get_by_text(
                BypassApprovalLocators.NO_RESULTS_TEXT, exact=False
            ).is_visible(timeout=2_000)
        except Exception:
            return False

    def get_bypass_flag_count(self) -> int:
        """Return the number of bypass-flag cells visible in the current grid view."""
        return self.bypass_flag_cells.count()

    def click_bypass_flag(self, row_index: int = 0, timeout: int = 10_000) -> None:
        """Click the bypass approval flag button for *row_index* (0-based).

        Uses an explicit timeout because the flag button is conditionally active.
        Waits for network idle after clicking so any API call completes.
        """
        self.bypass_flag_cells.nth(row_index).locator("button").click(timeout=timeout)
        self.page.wait_for_load_state("networkidle", timeout=10_000)

    def click_bypass_and_open_details(self, row_index: int = 0) -> None:
        """Toggle the bypass flag and navigate to invoice details from the SAME row.

        Both DOM clicks are performed inside one synchronous JavaScript evaluation
        so the grid cannot re-sort (and change row positions) between the bypass
        toggle and the invoice-link click.  This is the preferred method when
        the grid contains rows with duplicate invoice numbers, or when the
        Bypass Approval column sort is active.

        The bypass XHR fires in the background; ``wait_for_load_state("networkidle")``
        after navigation ensures the API response (and its History entry) is
        recorded before the test checks the History tab.
        """
        self.page.evaluate(
            """(rowIndex) => {
                const rows = document.querySelectorAll('[data-testid="table-row"]');
                const row = rows[rowIndex];
                if (!row) return;
                // Click bypass flag to toggle its state
                row.querySelector('td.dashboard-table-urgentBypass button')?.click();
                // Immediately click the invoice-number link in the same row
                // (before any React re-render / grid re-sort can occur)
                row.querySelector('td.dashboard-table-invoiceNo button')?.click();
            }""",
            row_index,
        )
        # Wait for the SPA to navigate to the invoice detail URL
        self.page.wait_for_url("**/invoice**", timeout=30_000)
        # networkidle ensures the background bypass XHR has also completed
        self.page.wait_for_load_state("networkidle", timeout=30_000)

    def is_bypass_flag_active(self, row_index: int = 0) -> bool:
        """Return True if the bypass flag at *row_index* is in the active state.

        The app adds one extra CSS-in-JS class token to the button element when
        the flag is active; inactive buttons have 12 filtered class tokens while
        active ones have 13.  This is detected via JavaScript evaluation so the
        test does not depend on the exact generated class name (which can change
        with CSS-in-JS rebuilds).
        """
        return self.page.evaluate(
            """(rowIndex) => {
                const buttons = document.querySelectorAll(
                    'td.dashboard-table-urgentBypass button'
                );
                if (!buttons[rowIndex]) return false;
                const classes = buttons[rowIndex].className.split(/\\s+/).filter(Boolean);
                // Active: 13 class tokens; Inactive: 12 class tokens.
                return classes.length > 12;
            }""",
            row_index,
        )

    def get_invoice_number_in_row(self, row_index: int = 0) -> str:
        """Return the invoice number text shown in the grid for *row_index*."""
        return (
            self.invoice_no_cells.nth(row_index).locator("button").text_content() or ""
        ).strip()

    def get_invoice_url_for_row(self, row_index: int = 0) -> str:
        """Return the detail-page URL for the invoice at *row_index*.

        Clicks the invoice-number link, records the navigation URL (which
        contains the UUID), then returns to the dashboard.  This is the only
        reliable way to obtain the invoice UUID when the DOM exposes no
        unique identifier on the table row.
        """
        with self.page.expect_navigation(wait_until="commit", timeout=20_000):
            self.invoice_no_cells.nth(row_index).locator("button").first.click(
                timeout=10_000
            )
        invoice_url = self.page.url
        self.page.go_back(wait_until="networkidle", timeout=30_000)
        return invoice_url

    def navigate_to_invoice_url(self, invoice_url: str) -> None:
        """Navigate directly to a previously captured invoice detail URL."""
        self.page.goto(invoice_url, wait_until="networkidle", timeout=30_000)

    def open_invoice_details(self, row_index: int = 0, timeout: int = 10_000) -> None:
        """Click the invoice-number link to navigate to the invoice details page."""
        self.invoice_no_cells.nth(row_index).locator("button").click(timeout=timeout)
        self.page.wait_for_load_state("networkidle", timeout=30_000)

    def open_specific_invoice_details(self, invoice_number: str) -> None:
        """Navigate to the details page for the invoice whose number matches *invoice_number*.

        This is preferred over ``open_invoice_details(row_index)`` when the grid
        may re-sort after a bypass flag toggle (which would shift row positions).
        Uses `.first` to handle grids where the same invoice number appears in
        multiple rows (duplicates are possible in some data states).
        """
        self.invoice_no_cells.filter(
            has=self.page.get_by_text(invoice_number, exact=True)
        ).locator("button").first.click(timeout=10_000)
        self.page.wait_for_load_state("networkidle", timeout=30_000)

    # -------------------------------------------------------------------------
    # Detail page — tabs, approve, history
    # -------------------------------------------------------------------------

    def is_approve_button_visible(self) -> bool:
        """Return True if the Approve button is visible on the details page."""
        try:
            return self.approve_button.is_visible(timeout=5_000)
        except Exception:
            return False

    def is_approve_button_enabled(self) -> bool:
        """Return True if the Approve button is present and not disabled."""
        try:
            return self.approve_button.is_enabled(timeout=5_000)
        except Exception:
            return False

    def click_approve_button(self) -> bool:
        """Click the Approve button, handle the confirmation dialog, and capture the result.

        Two-step flow:
          Step 1: Click the main "Approve" button — a confirmation dialog appears:
                  "Approve invoice XXXXXXXX / Are you sure you want to approve this
                   invoice? This action cannot be undone."
          Step 2: Click "Approve Invoice" in that dialog — a toast/alert appears
                  with either a success message or an error.

        The final toast text is stored in self._last_approve_response so that
        get_approve_popup_text() can return it.

        Returns True if the whole flow completed (even if the server returned an
        error — that is a valid observable result). Returns False and emits a
        warning only if the click itself raised an exception.
        Network-mutating method — caller should assert the return value.
        """
        self._last_approve_response = ""
        try:
            # Step 1: Click the main Approve button
            self.approve_button.click(timeout=10_000)

            # Step 2: Wait for the confirmation dialog's "Approve Invoice" button
            # and click it.  Using the exact XPath the app exposes rather than
            # role-based lookup to avoid matching the OneTrust overlay dialog.
            approve_invoice_btn = self.page.locator("//button[text()='Approve Invoice']")
            approve_invoice_btn.wait_for(state="visible", timeout=10_000)

            # Capture the dialog message text before clicking
            try:
                dialog_msg = (
                    self.page.locator("//button[text()='Approve Invoice']")
                    .locator("xpath=ancestor::*[@role='dialog'][1]")
                    .text_content(timeout=1_000) or ""
                ).strip()
            except Exception:
                dialog_msg = "Approve invoice confirmation dialog"

            approve_invoice_btn.click(timeout=5_000)

            # Wait for the follow-up alert toast (success or error)
            try:
                self.page.wait_for_selector('[role="alert"]', timeout=8_000)
                alert_el = self.page.locator('[role="alert"]').first
                self._last_approve_response = (
                    alert_el.inner_text(timeout=3_000) or ""
                ).strip()
            except Exception:
                # No toast appeared; store the dialog message as the response
                self._last_approve_response = dialog_msg

            return True

        except Exception as exc:
            warnings.warn(f"[BypassApprovalPage] click_approve_button failed: {exc}")
            return False

    def get_approve_popup_text(self) -> str:
        """Return the response text captured during click_approve_button().

        Returns the final toast/alert text that appeared after clicking
        "Approve Invoice" in the confirmation dialog, or the dialog's own
        message if no toast appeared. Returns an empty string if nothing
        was captured.
        """
        if hasattr(self, "_last_approve_response") and self._last_approve_response:
            return self._last_approve_response

        # Live fallback: check for a visible alert
        try:
            alert = self.page.locator('[role="alert"]').first
            if alert.is_visible(timeout=1_000):
                return (alert.inner_text() or "").strip()
        except Exception:
            pass

        return ""

    def navigate_to_history_tab(self) -> None:
        """Click the History tab on the invoice detail page."""
        self.history_tab.click(timeout=10_000)
        self.page.wait_for_load_state("networkidle", timeout=10_000)

    def get_history_panel_text(self) -> str:
        """Return the full text content of the active History tab panel.

        The panel contains all history entries rendered as paragraphs
        (User / Date / Action).  Asserting on plain text is the most robust
        approach as no stable test-ids are present on individual entries.
        """
        self.history_panel.wait_for(state="visible", timeout=10_000)
        return (self.history_panel.text_content() or "").strip()

    # -------------------------------------------------------------------------
    # Navigation helpers
    # -------------------------------------------------------------------------

    def navigate_back_to_dashboard(self) -> None:
        """Navigate back to the dashboard from any page.

        Uses ``page.go_back()`` first (preferred for preserving browser history),
        but falls back to a direct ``goto(BASE_URL)`` if the back navigation
        does not land on the dashboard within the timeout.  This is more
        reliable than clicking the app's Back button, which can be temporarily
        hidden or re-rendered during History tab interactions.
        """
        from utils.config import BASE_URL
        self.page.goto(BASE_URL, wait_until="networkidle", timeout=30_000)

    def reload_page(self) -> None:
        """Reload the current page and wait for network idle."""
        self.page.reload(wait_until="networkidle", timeout=30_000)
