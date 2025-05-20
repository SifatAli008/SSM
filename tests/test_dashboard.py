import pytest
from app.views.dashboard_view import DashboardPage

@pytest.fixture
def dashboard(qtbot):
    page = DashboardPage()
    qtbot.addWidget(page)
    return page

def test_dashboard_cards_update(dashboard):
    dashboard.update_all_cards()
    assert dashboard.revenue_card is not None
    assert dashboard.customer_card is not None
    assert dashboard.orders_card is not None
    # Check that card values are strings (UI updated)
    assert isinstance(dashboard.revenue_card.value_label.text(), str)
    assert isinstance(dashboard.customer_card.value_label.text(), str)
    assert isinstance(dashboard.orders_card.value_label.text(), str)

def test_dashboard_loading_indicator(qtbot, dashboard):
    dashboard.show()
    dashboard.show_loading()
    assert dashboard.loading_label.isVisible()
    dashboard.hide_loading()
    assert not dashboard.loading_label.isVisible() 