
import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from playwright.sync_api import expect

from pages.home_page import HomePage


pytestmark = [pytest.mark.bdd, pytest.mark.ui]

scenarios("product_search.feature")


@pytest.fixture
def home(page):
    """Open the product catalog and return its Page Object."""
    return HomePage(page).open()


@given("the customer is viewing the product catalog")
def customer_views_product_catalog(home):
    return home


@when(parsers.parse('the customer searches for "{keyword}"'))
def customer_searches_for_keyword(home, keyword):
    home.search(keyword)
    expect(home.search_completed).to_be_visible()


@then(parsers.parse(
    'the search results include products matching "{expected_keyword}"'
))
def search_results_include_keyword(home, expected_keyword):
    expect(home.product_names.first).to_be_visible()

    product_names = home.product_names.all_text_contents()

    assert len(product_names) > 0, "No products were displayed"

    for name in product_names:
        assert expected_keyword.lower() in name.lower(), (
            f"Product '{name}' does not contain '{expected_keyword}'"
        )


@then("the customer sees a message that no products were found")
def customer_sees_no_products_message(home):
    expect(home.no_results).to_have_text(
        "There are no products found."
    )
    expect(home.product_names).to_have_count(0)
