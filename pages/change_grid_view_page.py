import warnings
from playwright.sync_api import Page
from pages.dashboard_page import DashboardPage


class ChangeGridViewPage(DashboardPage):
    """
    Page Object for the Change Grid View workflow on the AP Invoice dashboard.
    Inherits all column-panel and grid methods from DashboardPage and adds
    aliases used by the change-grid-view test suite.
    """

    def __init__(self, page: Page):
        super().__init__(page)

    # ------------------------------------------------------------------
    # Aliases — keep the test-facing API readable
    # ------------------------------------------------------------------

    def open_change_grid_view_panel(self) -> None:
        # Removes the cookie banner overlay then opens the column settings panel.
        self.open_grid_settings()

    def move_column_to_active(self, column_name: str) -> None:
        # Selects the column in Available Columns and moves it to Active.
        self.move_available_column_to_active(column_name)

    def move_column_to_available(self, column_name: str) -> None:
        # Selects the column in Active Columns and moves it to Available.
        self.move_active_column_to_available(column_name)

    def is_column_visible_in_grid(self, column_name: str) -> bool:
        # Returns True when the column header is present in the dashboard grid.
        return self.is_column_header_visible(column_name)

    # ------------------------------------------------------------------
    # Safe-move helpers — skip gracefully when column is not in source list
    # ------------------------------------------------------------------

    def move_column_to_active_safe(self, column_name: str) -> bool:
        """
        Moves column_name from Available → Active only when it is currently
        in the Available list. Emits a warning and returns False when not found.
        """
        if column_name not in self.get_panel_column_list("Available Columns"):
            warnings.warn(
                f"[ChangeGridViewPage] '{column_name}' not in Available Columns — "
                "skipping move_to_active."
            )
            return False
        self.move_column_to_active(column_name)
        return True

    def move_column_to_available_safe(self, column_name: str) -> bool:
        """
        Moves column_name from Active → Available only when it is currently
        in the Active list. Emits a warning and returns False when not found.
        """
        if column_name not in self.get_panel_column_list("Active Columns"):
            warnings.warn(
                f"[ChangeGridViewPage] '{column_name}' not in Active Columns — "
                "skipping move_to_available."
            )
            return False
        self.move_column_to_available(column_name)
        return True

    # ------------------------------------------------------------------
    # Viewport / browser resize helper
    # ------------------------------------------------------------------

    def resize_browser_window(self, width: int, height: int) -> None:
        self.page.set_viewport_size({"width": width, "height": height})
