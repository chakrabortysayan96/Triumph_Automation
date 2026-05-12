class BypassApprovalLocators:
    """Stable selectors for the Bypass Approval / Urgent Flag feature."""

    # -------------------------------------------------------------------------
    # Dashboard
    # -------------------------------------------------------------------------

    # data-testid on the search input (confirmed via live MCP inspection).
    SEARCH_INPUT_TESTID = "search-bar-input"

    # CSS class on each <td> in the "Bypass Approval" column of the invoice grid.
    # Used as the root selector for every bypass-flag interaction on the dashboard.
    BYPASS_CELL_CSS = "td.dashboard-table-urgentBypass"

    # CSS class on each <td> in the "Invoice No." column.
    # The clickable invoice-number button lives directly inside this cell.
    INVOICE_NO_CELL_CSS = "td.dashboard-table-invoiceNo"

    # data-testid on the "Clear filters" button shown when the grid has no rows.
    CLEAR_FILTERS_TESTID = "clear-filters-button"

    # Element ID of the OneTrust cookie-consent overlay.
    # The overlay intercepts pointer events until removed via JavaScript.
    COOKIE_BANNER_ID = "onetrust-consent-sdk"

    # -------------------------------------------------------------------------
    # Invoice Detail Page
    # -------------------------------------------------------------------------

    # Button text / role names used to locate action buttons on the detail page.
    APPROVE_BUTTON_TEXT = "Approve"
    # Button inside the confirmation dialog that actually submits the approval.
    APPROVE_INVOICE_BUTTON_TEXT = "Approve Invoice"
    BACK_BUTTON_TEXT = "Back"

    # Tab names in the tablist on the detail page.
    HISTORY_TAB_TEXT = "History"
    DETAILS_TAB_TEXT = "Details"

    # Prefix of the <h3> heading on the detail page (e.g. "Invoice No. 12345").
    INVOICE_HEADING_PREFIX = "Invoice No."

    # -------------------------------------------------------------------------
    # History Tab Content
    # -------------------------------------------------------------------------

    # Action strings recorded in the History tab when the bypass flag is toggled.
    BYPASS_ENABLED_ACTION = "Urgent bypass approval flag enabled."
    BYPASS_DISABLED_ACTION = "Urgent bypass approval flag disabled."

    # -------------------------------------------------------------------------
    # No-results state
    # -------------------------------------------------------------------------

    # Heading shown when the grid has no matching rows (e.g. after a search).
    NO_RESULTS_TEXT = "No results found"

    # -------------------------------------------------------------------------
    # AP Invoice Management landing page
    # -------------------------------------------------------------------------

    # Main heading confirming the user is on the correct module.
    AP_INVOICE_HEADING = "AP Invoice Management"
