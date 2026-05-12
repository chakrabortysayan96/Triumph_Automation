class InvoiceDueDateLocators:
    """
    Locators for Invoice Due Date tests on the AP Invoice Management app.

    All CSS class names are confirmed via prior live inspection of the app;
    the `dashboard-table-*` naming convention matches other confirmed cells
    (e.g. dashboard-table-invoiceNo, dashboard-table-submitter).
    """

    # ── Dashboard ──────────────────────────────────────────────────────────
    SEARCH_INPUT_TESTID = "search-bar-input"
    COOKIE_BANNER_ID = "onetrust-consent-sdk"

    # CSS class on each <td> in the Invoice No. column (confirmed).
    INVOICE_NO_CELL_CSS = "td.dashboard-table-invoiceNo"

    # CSS class on each <td> in the Invoice Due Date column.
    # Confirmed via live DOM inspection: dashboard-table-dueDate
    INVOICE_DUE_DATE_CELL_CSS = "td.dashboard-table-dueDate"

    # CSS class on each <td> in the BU Country column.
    # Confirmed via live DOM inspection: dashboard-table-countryCode
    BU_COUNTRY_CELL_CSS = "td.dashboard-table-countryCode"

    # All data rows in the invoice grid.
    DASHBOARD_ROW_CSS = "table tbody tr"

    # MUI circular progress spinner shown while the grid reloads.
    LOADING_SPINNER_CSS = ".MuiCircularProgress-root"

    # No-results placeholder heading (shown when search/filter yields nothing).
    NO_RESULTS_TEXT = "No results found"

    # ── Invoice Details Page — view-mode (label `for` attribute) ────────────
    # Each detail field is rendered as:
    #   p[for="fieldFor"]  →  div.inline.align-middle  →  div.RUPldswjkpaxnk7J5NsV
    #     child[0] = label div, child[1] = value div  →  p.truncate (value text)
    # XPath pattern confirmed via live browser inspection on the preprod app.
    #
    # BU Country uses p[for='countryCode'] confirmed via live DOM inspection:
    #   p[for='countryCode'] → div.inline.align-middle → wrapper div
    #     wrapper.children[0] = label div
    #     wrapper.children[1] = value div → p.truncate (value text e.g. 'DK')
    # _get_field_value('countryCode') confirmed to return 'DK' for invoice 380-0063-00-01.
    BU_COUNTRY_FOR = "countryCode"
    INVOICE_DUE_DATE_FOR = "dueDate"
    INVOICE_RECEIPT_DATE_FOR = "invoiceStampDate"
    PAYMENT_TERMS_FOR = "paymentTerms"
    INVOICE_DATE_FOR = "invoiceDate"

    # ── Invoice Details Page — edit-mode (input name attributes) ─────────────
    # Confirmed by live DOM inspection in edit mode.
    INVOICE_RECEIPT_DATE_INPUT = "input[name='invoiceStampDate.value']"
    INVOICE_DATE_INPUT = "input[name='invoiceDate.value']"
    # Payment Terms is a MUI Autocomplete — interact via its visible text input.
    PAYMENT_TERMS_INPUT = "input[placeholder='Payment Terms']"

    # ── Exception country codes ─────────────────────────────────────────────
    # BU Country field value contains one of these strings for exception countries
    # (Sweden = SE, France = FR, Denmark = DK).
    EXCEPTION_COUNTRY_CODES = ("SE", "FR", "DK")
