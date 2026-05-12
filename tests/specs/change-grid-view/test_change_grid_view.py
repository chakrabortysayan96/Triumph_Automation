import pytest
from pages.login_page import LoginPage
from pages.change_grid_view_page import ChangeGridViewPage
from utils.config import BASE_URL, USERNAME, PASSWORD


class TestChangeGridView:

    def test_aiop_127465_change_grid_view_panel_opens_with_no_data(self, page):
        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        grid_view_page = ChangeGridViewPage(page)

        # TODO: Step 1 — Navigate to main dashboard page where no invoice records are present (0 records)
        # TODO: Step 2 — Click the 'Change Grid View' button
        # TODO: Step 3 — Verify the customization panel opens listing all available columns; columns can be selected or deselected

    def test_aiop_122784_customize_dashboard_negative_cases(self, page):
        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        grid_view_page = ChangeGridViewPage(page)

        # TODO: Step 1 — Navigate to dashboard; verify Change Grid View option is visible and clickable
        # TODO: Step 2 — Click Change Grid View icon; verify popup shows available/active columns and Apply/Cancel buttons
        # TODO: Step 3 — Rearrange columns in active area; move Po No., Supplier, Business Unit between areas
        # TODO: Step 4 — Close or dismiss the popup without clicking Apply
        # TODO: Step 5 — Verify no changes are applied to the dashboard; page loads with minimum delay

    def test_aiop_122783_customize_dashboard_different_browser(self, page):
        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        grid_view_page = ChangeGridViewPage(page)

        # TODO: Step 1 — Navigate to dashboard with valid credentials in Chrome and Edge
        # TODO: Step 2 — Click Change Grid View icon; verify popup opens with available/active columns
        # TODO: Step 3 — Move Invoice No., Supplier, BU Country to available; add Invoice Due Date, Payment Terms, Payment Method to active
        # TODO: Step 4 — Click Apply; verify rearranged columns appear on dashboard
        # TODO: Step 5 — Minimize, Maximize, Zoom in, Zoom out the browser; verify panel controls remain visible and clickable
        # TODO: Step 6 — Refresh browser; clear cookies; re-login; verify customized column selection is maintained

    def test_aiop_122413_customize_dashboard_browser_settings(self, page):
        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        grid_view_page = ChangeGridViewPage(page)

        # TODO: Step 1 — Navigate to dashboard; verify Change Grid View option is visible and clickable
        # TODO: Step 2 — Click the Change Grid View icon; verify popup opens with available/active columns
        # TODO: Step 3 — Minimize, Maximize, Zoom in, Zoom out the browser; verify Save Grid View/Cancel/arrows remain visible and clickable
        # TODO: Step 4 — Refresh browser; clear cookies; re-login; verify customized column selection and order is maintained

    def test_aiop_122385_customize_dashboard_remove_active_column(self, page):
        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        grid_view_page = ChangeGridViewPage(page)

        # TODO: Step 1 — Navigate to dashboard; verify Change Grid View option is visible and clickable
        # TODO: Step 2 — Click the Change Grid View icon; verify popup opens with available/active columns
        # TODO: Step 3 — Remove Invoice No., Supplier, Business Unit from active area to available area
        # TODO: Step 4 — Click Apply; verify removed columns are no longer visible on the dashboard
        # TODO: Step 5 — Refresh browser; clear cookies; re-login; verify customized column selection is maintained

    def test_aiop_122382_customize_dashboard_add_available_column(self, page):
        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        grid_view_page = ChangeGridViewPage(page)

        # TODO: Step 1 — Navigate to dashboard; verify Change Grid View option is visible and clickable
        # TODO: Step 2 — Click the Change Grid View icon; verify popup opens with scrollable available/active lists
        # TODO: Step 3 — Move Payment Terms, Payment Method, Supplier ID from available area to active area
        # TODO: Step 4 — Click Apply; verify added columns appear on the dashboard
        # TODO: Step 5 — Refresh browser; clear cookies; re-login; verify customized column selection is maintained
