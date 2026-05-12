class ColumnFilterLocators:
    """
    Locators for the column-level filter controls on the AP Invoice Management dashboard.

    Filter panel architecture (MUI Popover):
      - The filter icon is a MUI IconButton (`button.MuiIconButton-root`) rendered inside
        each filterable column header `<th>`.
      - Clicking the icon opens a MUI Popover that is portal-rendered to `<body>` with
        the class `.MuiPopover-root.MuiModal-root`.
      - Inside the popover: a search `<input>`, a list of MUI Checkboxes, and
        "Clear All" / "Apply" `<button>` controls.
      - The Apply button is DISABLED when: (a) no checkboxes are selected and the search
        box is empty, or (b) the search term yields zero matching values.
    """

    # ---- Column header -------------------------------------------------------
    # Sort/title button present in every column header.
    COLUMN_HEADER_TITLE_BUTTON = "button.header-title"

    # Filter icon button (MUI IconButton) present ONLY in filterable column headers.
    # Used to open the filter panel for a column.
    FILTER_ICON_BUTTON = "button.MuiIconButton-root"

    # ---- Filter panel (MUI Popover) ------------------------------------------
    # Root element of the filter popover, portal-rendered to <body>.
    FILTER_POPOVER = ".MuiPopover-root.MuiModal-root"

    # Search / type-ahead input within the filter panel.
    # Placeholder follows the pattern: "Search <Column Name>".
    FILTER_SEARCH_INPUT = "input:not([type='checkbox'])"

    # Individual value checkboxes.  Each has value=<option text>.
    # MUI hides the native input (opacity:0); interact via check(force=True).
    FILTER_CHECKBOX = "input[type='checkbox']"

    # Action buttons inside the filter panel.
    FILTER_APPLY_BUTTON_TEXT = "Apply"
    FILTER_CLEAR_ALL_BUTTON_TEXT = "Clear All"

    # ---- Grid ----------------------------------------------------------------
    # Data rows in the invoice grid table.
    GRID_DATA_ROWS = "tbody tr"

    # ---- Column name mapping (UI label → exact text in column header) --------
    # Columns the product requires to carry a filter icon.
    # "PO Type" is omitted here because it is not present in the default active
    # columns view and must first be enabled via Change Grid View.
    FILTERABLE_COLUMNS = {
        "Urgent Flag":      "Priority",          # Priority shows urgency: High/Medium/Low
        "Invoice Due Date": "Invoice Due Date",
        "Submitter":        "Submitter",
        "Requester":        "Requester",
        "Business Unit":    "Business Unit",
        "Supplier":         "Supplier",
        "BU Country":       "BU Country",
        "PO Number":        "PO No.",
        "Invoice Number":   "Invoice No.",
        "Inv Src Doc":      "Invoice Src. Doc.",
        "Status":           "Status",
    }

    # A column that must NOT have a filter icon (used by TC-014).
    NON_FILTERABLE_COLUMN = "Invoice Date"

    # ---- Known filter option values (verified via live UI inspection) --------
    # Invoice Src. Doc. options (value as shown in the filter dropdown).
    INV_SRC_DOC_NON_PO = "Non PO Invoice"

    # Status options.
    STATUS_PENDING_APPROVAL = "Pending Approval"
    STATUS_PENDING_BUSINESS_REVIEW = "Pending Business Review"

    # Cookie banner SDK element ID (must be removed before interacting with grid).
    COOKIE_SDK_ID = "onetrust-consent-sdk"
