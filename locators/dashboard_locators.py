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

    # --- Dashboard Column Header Verification ---
    # CSS class shared by all sortable column header buttons in the grid.
    # Used to check whether a column header is present after applying changes.
    COLUMN_HEADER_CLASS = "header-title"
