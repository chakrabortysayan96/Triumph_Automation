import pathlib
from playwright.sync_api import Page
from pages.base_page import BasePage
from locators.dashboard_locators import DashboardLocators
from utils.config import DOWNLOADS_DIR


class DashboardPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

    def get_page_title(self) -> str:
        # Returns the browser tab title of the currently loaded dashboard page.
        return self.page.title()

    def is_ap_invoice_text_visible(self) -> bool:
        # Checks whether the AP Invoice Management heading is visible on the page.
        return self.is_text_visible(DashboardLocators.AP_INVOICE_TEXT)

    def get_ap_invoice_elements(self) -> list:
        # Returns the inner text of every element that matches the
        # AP Invoice Management label (useful for asserting count or content).
        locator = self.page.get_by_text(DashboardLocators.AP_INVOICE_TEXT, exact=False)
        return [locator.nth(i).inner_text() for i in range(locator.count())]

    # -------------------------------------------------------------------------
    # Cookie Banner
    # The OneTrust SDK injects a full-page overlay that blocks all pointer
    # events until dismissed. Removing it via JS is the most reliable approach.
    # -------------------------------------------------------------------------

    def _dismiss_cookie_banner(self):
        self.page.evaluate(
            f"document.getElementById('{DashboardLocators.COOKIE_SDK_ID}')?.remove()"
        )
        self.page.wait_for_timeout(300)

    # -------------------------------------------------------------------------
    # Grid View / Column Settings
    # Methods to open the Change Grid View panel, move columns between the
    # Available and Active lists, and apply the configuration.
    # -------------------------------------------------------------------------

    def open_grid_settings(self):
        # Dismisses the cookie overlay then clicks the column config button
        # (top-right of the grid toolbar). Waits until the panel heading is
        # visible before returning so callers can interact immediately.
        self._dismiss_cookie_banner()
        self.page.locator(
            f'[data-testid="{DashboardLocators.CHANGE_GRID_VIEW_BUTTON_TESTID}"]'
        ).click()
        self.page.get_by_text(DashboardLocators.COLUMN_SETTINGS_HEADING, exact=False).wait_for(
            state="visible", timeout=15000
        )

    def _get_column_section(self, label: str):
        # Returns the parent container of the list identified by `label`
        # ("Available Columns" or "Active Columns"), scoping all item lookups
        # so we never match a column name in the wrong list.
        return self.page.locator("label").filter(has_text=label).locator("..")

    def move_active_column_to_available(self, column_name: str):
        # Selects the column from the Active list then clicks the left-arrow
        # button to move it into the Available list.
        section = self._get_column_section(DashboardLocators.ACTIVE_COLUMNS_LABEL)
        section.get_by_role("button", name=column_name, exact=True).click()
        self.page.locator(
            f'[data-testid="{DashboardLocators.MOVE_TO_AVAILABLE_BUTTON_TESTID}"]'
        ).click()

    def move_available_column_to_active(self, column_name: str):
        # Selects the column from the Available list then clicks the right-arrow
        # button to move it into the Active list.
        section = self._get_column_section(DashboardLocators.AVAILABLE_COLUMNS_LABEL)
        section.get_by_role("button", name=column_name, exact=True).click()
        self.page.locator(
            f'[data-testid="{DashboardLocators.MOVE_TO_ACTIVE_BUTTON_TESTID}"]'
        ).click()

    def apply_column_settings(self):
        # Clicks Apply to confirm the column configuration, waits for the
        # panel to close, then waits for the dashboard grid to finish reloading.
        self.page.get_by_role("button", name=DashboardLocators.APPLY_BUTTON).click()
        self.page.get_by_text(
            DashboardLocators.COLUMN_SETTINGS_HEADING, exact=False
        ).wait_for(state="hidden", timeout=15000)
        self.page.wait_for_load_state("networkidle", timeout=30000)

    def cancel_column_settings(self) -> None:
        # Clicks Cancel to discard pending changes and waits for the panel to close.
        self.page.get_by_test_id(DashboardLocators.CANCEL_BUTTON_TESTID).click()
        self.page.get_by_text(
            DashboardLocators.COLUMN_SETTINGS_HEADING, exact=False
        ).wait_for(state="hidden", timeout=10000)

    def is_panel_open(self) -> bool:
        # Returns True when the column settings panel heading is visible.
        try:
            return self.page.get_by_text(
                DashboardLocators.COLUMN_SETTINGS_HEADING, exact=False
            ).is_visible(timeout=3000)
        except Exception:
            return False

    def get_panel_column_list(self, list_label: str) -> list:
        # Returns the column names currently shown in the specified panel list
        # ("Available Columns" or "Active Columns").
        section = self._get_column_section(list_label)
        items = section.get_by_role("button").all()
        return [item.text_content().strip() for item in items]

    def get_grid_record_count(self) -> int:
        # Returns the number of data rows currently visible in the dashboard grid.
        return self.page.locator("table tbody tr").count()

    def clear_cookies_and_relogin(self, url: str, username: str, password: str) -> None:
        # Clears all browser cookies then performs a fresh login, simulating a
        # new session while reusing the same page object.
        from pages.login_page import LoginPage
        self.page.context.clear_cookies()
        login_page = LoginPage(self.page)
        login_page.navigate(url)
        login_page.login(username, password)

    # -------------------------------------------------------------------------
    # Column Header Verification
    # Checks presence or absence of a column header in the dashboard grid
    # after column settings have been applied.
    # -------------------------------------------------------------------------

    def is_column_header_visible(self, column_name: str) -> bool:
        # Searches for a column header button matching `column_name` inside
        # the grid. Returns True if at least one matching header is found.
        return (
            self.page.locator(f".{DashboardLocators.COLUMN_HEADER_CLASS}")
            .filter(has_text=column_name)
            .count() > 0
        )

    # -------------------------------------------------------------------------
    # Column Sorting
    # Methods to click sortable column headers, read the current sort
    # direction from the indicator image, and scrape column cell values.
    # -------------------------------------------------------------------------

    def is_column_header_sortable(self, column_name: str) -> bool:
        # Returns True if the named column header contains the sortable CSS
        # class, confirming the app treats it as a sortable column.
        return (
            self.page.locator(f".{DashboardLocators.SORTABLE_HEADER_CLASS}")
            .filter(has_text=column_name)
            .count() > 0
        )

    def click_column_header(self, column_name: str) -> None:
        # Clicks the sort button for the named column, then waits for the
        # grid rows to re-appear so the sort direction is readable.
        sort_btn = (
            self.page.locator(f".{DashboardLocators.SORTABLE_HEADER_CLASS}")
            .filter(has_text=column_name)
            .first
        )
        sort_btn.click(timeout=15000)
        # Wait for at least one data row to be visible after the sort API call.
        self.page.locator("table tbody tr").first.wait_for(
            state="visible", timeout=30000
        )

    def get_sort_direction(self, column_name: str) -> str | None:
        # Returns 'ascending', 'descending', or None by inspecting the
        # accessible name of the <th> columnheader element.
        # The app sets the columnheader accessible name to include
        # "in ascending order" or "in descending order" after a sort click.
        # This works for both img-based and SVG-based sort indicators.
        try:
            asc_count = self.page.get_by_role(
                "columnheader", name=f"{column_name} in ascending"
            ).count()
            if asc_count > 0:
                return "ascending"
            desc_count = self.page.get_by_role(
                "columnheader", name=f"{column_name} in descending"
            ).count()
            if desc_count > 0:
                return "descending"
            return None
        except Exception:
            return None

    def get_column_values(self, column_name: str) -> list[str]:
        # Returns all visible cell values for the named column by finding
        # the column index from the header row and reading each body cell.
        headers = self.page.locator("table thead th").all()
        col_index = None
        for i, th in enumerate(headers):
            inner = th.inner_text().strip().split("\n")[0]
            if column_name in inner:
                col_index = i
                break
        if col_index is None:
            return []
        rows = self.page.locator("table tbody tr").all()
        values = []
        for row in rows:
            cells = row.locator("td").all()
            if col_index < len(cells):
                values.append(cells[col_index].inner_text().strip())
        return values

    def is_grid_horizontal_scrollable(self) -> bool:
        # Returns True when the grid scroll container's total content width
        # exceeds its visible client width, confirming a horizontal scrollbar
        # is present. Uses the stable partial-class selector for the table
        # wrapper and walks up one level to reach the overflow-x:auto parent.
        # Confirmed via live DOM inspection: TABLE_WRAP_CLASS_SUBSTRING parent
        # has scrollWidth=2773 vs clientWidth=944 when all columns are active.
        return self.page.evaluate(
            f"""() => {{
                const tableWrap = document.querySelector(
                    '[class*="{DashboardLocators.TABLE_WRAP_CLASS_SUBSTRING}"]'
                );
                const scrollEl = tableWrap?.parentElement;
                return scrollEl ? scrollEl.scrollWidth > scrollEl.clientWidth : false;
            }}"""
        )

    def is_grid_vertical_scrollable(self) -> bool:
        # Returns True when the grid container's content height exceeds the
        # visible height, confirming a vertical scrollbar is present.
        return self.page.evaluate(
            f"""() => {{
                const tableWrap = document.querySelector(
                    '[class*="{DashboardLocators.TABLE_WRAP_CLASS_SUBSTRING}"]'
                );
                const scrollEl = tableWrap?.parentElement;
                return scrollEl ? scrollEl.scrollHeight > scrollEl.clientHeight : false;
            }}"""
        )

    def move_all_available_to_active(self) -> None:
        # Moves every column in the Available Columns list to Active Columns.
        # No-op when Available is already empty (all columns in Active).
        # The panel must already be open when this is called.
        available = self.get_panel_column_list(DashboardLocators.AVAILABLE_COLUMNS_LABEL)
        for col in available:
            self.move_available_column_to_active(col)

    def clear_active_columns_except(self, keep_columns: list) -> None:
        # Moves all Active Columns NOT in keep_columns to Available Columns.
        # Used to configure a minimal column set that fits within the viewport
        # (e.g., for TC-016 no-scrollbar verification).
        # The panel must already be open when this is called.
        active = self.get_panel_column_list(DashboardLocators.ACTIVE_COLUMNS_LABEL)
        for col in active:
            if col not in keep_columns:
                self.move_active_column_to_available(col)

    # -------------------------------------------------------------------------
    # Export as Excel
    # -------------------------------------------------------------------------

    def download_excel(self) -> pathlib.Path:
        # Clicks the Export as Excel button, waits for the browser download
        # event, saves the file to DOWNLOADS_DIR, and returns the file path.
        downloads_dir = pathlib.Path(DOWNLOADS_DIR)
        downloads_dir.mkdir(parents=True, exist_ok=True)
        with self.page.expect_download(timeout=60_000) as download_info:
            self.page.get_by_test_id(
                DashboardLocators.EXPORT_EXCEL_BUTTON_TESTID
            ).click(timeout=10_000)
        download = download_info.value
        dest = downloads_dir / download.suggested_filename
        download.save_as(str(dest))
        return dest

    def get_all_column_headers(self) -> list:
        # Returns the text label of every column header currently rendered
        # in the grid's <thead>.  Strips whitespace and excludes empty strings.
        self.page.locator("table thead th").first.wait_for(
            state="visible", timeout=15_000
        )
        raw = self.page.locator("table thead th").all_text_contents()
        return [h.strip() for h in raw if h.strip()]

    def click_invoice_row_by_index(self, index: int = 0) -> None:
        # Clicks the Invoice No. button in the nth (0-based) data row to open
        # its details page.  Uses the scoped td CSS class so only the invoice
        # number link inside that specific row is targeted, matching the pattern
        # established in SubmitterEmailPopoverPage.open_invoice_by_index().
        row = self.page.locator("table tbody tr").nth(index)
        row.locator("td.dashboard-table-invoiceNo button").first.click(timeout=15_000)
        self.page.wait_for_load_state("networkidle", timeout=30_000)

    # -------------------------------------------------------------------------
    # Invoice-level row helpers (used by exception country due date tests)
    # These methods locate a specific invoice row by invoice number and read
    # the value of a particular cell from that row.
    # -------------------------------------------------------------------------

    def _get_invoice_row(self, invoice_number: str):
        # Returns a Locator scoped to the <tr> that contains the given invoice
        # number in its Invoice No. cell. Uses the confirmed CSS class for the
        # invoice-number cell to scope the ancestor-tr lookup.
        from locators.invoice_due_date_locators import InvoiceDueDateLocators
        return (
            self.page.locator(InvoiceDueDateLocators.INVOICE_NO_CELL_CSS)
            .filter(has_text=invoice_number)
            .first
            .locator("xpath=ancestor::tr[1]")
        )

    def get_invoice_due_date_for_invoice(self, invoice_number: str) -> str:
        # Returns the text value of the Invoice Due Date cell for the given
        # invoice row. Returns an empty string when the cell is blank.
        from locators.invoice_due_date_locators import InvoiceDueDateLocators
        row = self._get_invoice_row(invoice_number)
        return row.locator(InvoiceDueDateLocators.INVOICE_DUE_DATE_CELL_CSS).first.inner_text().strip()

    def get_bu_country_for_invoice(self, invoice_number: str) -> str:
        # Returns the text value of the BU Country cell for the given invoice
        # row. The CSS class follows the dashboard-table-<fieldName> convention.
        from locators.invoice_due_date_locators import InvoiceDueDateLocators
        row = self._get_invoice_row(invoice_number)
        return row.locator(InvoiceDueDateLocators.BU_COUNTRY_CELL_CSS).first.inner_text().strip()

    def click_invoice_by_number(self, invoice_number: str) -> None:
        # Clicks the Invoice No. button in the row matching the given invoice
        # number and waits for the details page to finish loading.
        from locators.invoice_due_date_locators import InvoiceDueDateLocators
        row = self._get_invoice_row(invoice_number)
        row.locator("td.dashboard-table-invoiceNo button").first.click(timeout=15_000)
        self.page.wait_for_load_state("networkidle", timeout=30_000)
