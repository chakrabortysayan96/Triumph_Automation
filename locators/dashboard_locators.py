class DashboardLocators:

    # --- AP Invoice Management Section ---
    # Main heading/label that identifies the AP Invoice Management module.
    # Used to verify the dashboard has loaded the correct section.
    AP_INVOICE_TEXT = "AP Invoice Management"

    # --- Cookie Banner ---
    # OneTrust cookie consent SDK element that renders a full-page overlay.
    # Must be removed via JavaScript before any grid interaction is possible.
    COOKIE_SDK_ID = "onetrust-consent-sdk"

    # --- Change Grid View Button ---
    # Settings icon button in the top-right of the grid toolbar.
    # Identified by data-testid; opens the column selection panel.
    CHANGE_GRID_VIEW_BUTTON_TESTID = "dashboard-column-config-btn"

    # --- Column Settings Panel ---
    # Heading text of the panel that appears after clicking Change Grid View.
    # Used to confirm the panel has fully opened before interacting with it.
    COLUMN_SETTINGS_HEADING = "Select the columns to be displayed"

    # Labels of the two column lists inside the panel.
    # These labels scope item lookups so we never accidentally pick
    # a column name from the wrong list.
    AVAILABLE_COLUMNS_LABEL = "Available Columns"
    ACTIVE_COLUMNS_LABEL = "Active Columns"

    # =========================================================================
    # CONFIGURE HERE — update only these two fields to change which columns
    # are swapped and verified in test_grid_column_swap.
    #
    #   ACTIVE_STATUS_COLUMN        → must currently exist in Active Columns.
    #                                 It will be moved to Available, and the
    #                                 test will assert it is NOT in the dashboard.
    #
    #   AVAILABLE_INVOICE_TYPE_COLUMN → must currently exist in Available Columns.
    #                                   It will be moved to Active, and the
    #                                   test will assert it IS in the dashboard.
    # =========================================================================
    ACTIVE_STATUS_COLUMN          = "Status"
    AVAILABLE_INVOICE_TYPE_COLUMN = "Invoice Type"

    # --- Column Move Buttons ---
    # Right-arrow button (→): moves the selected item from Available → Active.
    MOVE_TO_ACTIVE_BUTTON_TESTID = "move-right-button"

    # Left-arrow button (←): moves the selected item from Active → Available.
    MOVE_TO_AVAILABLE_BUTTON_TESTID = "move-left-button"

    # --- Apply Button ---
    # Confirms the column configuration and reloads the dashboard grid.
    APPLY_BUTTON = "Apply"
    APPLY_BUTTON_TESTID = "apply-button"

    # --- Cancel Button ---
    # Discards any pending column changes and closes the panel.
    CANCEL_BUTTON_TESTID = "cancel-button"

    # --- Dashboard Column Header Verification ---
    # CSS class shared by all sortable column header buttons in the grid.
    # Used to check whether a column header is present after applying changes.
    COLUMN_HEADER_CLASS = "header-title"

    # --- Column Sorting ---
    # CSS compound-class selector (dot notation) for sortable column header
    # buttons. Non-sortable columns (e.g., Notes) do NOT have this class.
    # Value deliberately omits the leading dot so callers prepend it:
    #   f".{SORTABLE_HEADER_CLASS}"  →  ".header-title.sortable"
    SORTABLE_HEADER_CLASS = "header-title.sortable"

    # The img alt text injected by the app to indicate sort direction.
    # Confirmed via live inspection: values are exactly these strings.
    SORT_ASC_ALT  = "in ascending order"
    SORT_DESC_ALT = "in descending order"

    # data-testid on every <th> cell — used to scope column-header queries.
    TABLE_HEADER_CELL_TESTID = "table-header-cell"

    # The column that is non-sortable by design (confirmed live).
    NOTES_COLUMN_NAME = "Notes"

    # --- Export as Excel Button ---
    # data-testid confirmed via live inspection.
    EXPORT_EXCEL_BUTTON_TESTID = "s2pim-table-invoices-export-as-excel-btn"

    # --- Priority filter values (confirmed via live inspection) ---
    PRIORITY_HIGH    = "High"
    PRIORITY_MEDIUM  = "Medium"
    PRIORITY_LOW     = "Low"

    # --- Export CSV column headers (confirmed via live download, 2026-05-11) ---
    # The Export as Excel button downloads a .csv file.  These are the exact
    # column header strings that appear in row 1 of the downloaded file.
    # Independent of the Change Grid View configuration — the export always
    # includes this fixed server-side column set.
    EXPECTED_EXPORT_HEADERS = (
        "System ID",
        "Invoice No.",
        "PO No.",
        "PO Type",
        "Supplier",
        "Invoice Src. Doc.",
        "Business Unit",
        "Invoice Date",
        "Invoice Due Date",
        "Currency",
        "WHT Code",
        "IRN / FSI",
        "Payment Reference",
        "Tax Point Date",
        "Currency Key",
        "Gross Amount",
        "Submitter",
        "Requester",
        "Requester Email",
        "Priority",
        "Status",
        "Notes",
    )

    # --- Horizontal Scrollbar Detection ---
    # Stable CSS selector (partial class match) for the wrapper div that directly
    # contains the <table>. Its *parent* element is the overflow-x:auto scroll
    # container. Confirmed live: class includes "aiops-table-wrap" (stable BEM
    # token) alongside a CSS-module hash.
    TABLE_WRAP_CLASS_SUBSTRING = "aiops-table-wrap"

    # --- Due Date Dashboard & Sort ---
    # Column header names used for position and sort verification.
    INVOICE_DUE_DATE_COL_HEADER = "Invoice Due Date"
    INVOICE_DATE_COL_HEADER     = "Invoice Date"
