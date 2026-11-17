
import pytest
from pages.login_page import LoginPage
from pages.account_page import AccountPage
from playwright.sync_api import expect

from pages.home_page import HomePage
import re
from urllib.parse import parse_qs, urlparse

from pages.contact_page import ContactPage

# ---------------------------------------------------------
# 1. DANH SÁCH VÀ TÌM KIẾM

@pytest.mark.ui
def test_search_unknown_keyword_shows_no_results_message(page):
    """Goal: search for a keyword that does not exist.
    Precondition: none.
    Expected: no-results message is displayed and zero product cards."""
    home = HomePage(page).open().search("zzz-no-such-tool")

    expect(home.no_results).to_have_text(
        "There are no products found."
    )
    expect(home.product_names).to_have_count(0)


@pytest.mark.ui
@pytest.mark.parametrize("order", ["price,asc", "price,desc"])
def test_sort_by_price_orders_products(page, order):
    """Goal: sort products by price.
    Precondition: products are available.
    Expected: product prices are sorted in the selected direction."""
    home = HomePage(page).open()

    expect(home.product_names.first).to_be_visible()
    home.sort_by(order)
    expect(home.sorting_completed).to_be_visible()

    prices = home.prices()

    assert prices == sorted(
        prices,
        reverse=order.endswith("desc")
    ), prices


# ---------------------------------------------------------
# 2. BỘ LỌC

@pytest.mark.ui
def test_filter_by_hammer_category_shows_only_hammers(page):
    """Goal: filter products by Hammer category.
    Precondition: Hammer category is available.
    Expected: every displayed product name contains hammer."""
    home = HomePage(page).open()

    home.filter_by_category("Hammer")

    expect(home.product_names).to_have_count(7)

    for name in home.product_names.all_text_contents():
        assert "hammer" in name.lower(), name

# ---------------------------------------------------------
# 3. CHI TIẾT SẢN PHẨM

@pytest.mark.ui
def test_product_detail_shows_selected_product_name_and_price(page):
    """Goal: verify product details.
    Precondition: at least one product is available.
    Expected: detail page displays the selected product name and price."""
    home = HomePage(page).open()

    product_name = home.product_names.first.inner_text()
    product_price = home.prices()[0]

    product = home.open_product(product_name)

    expect(product.name).to_have_text(product_name)
    assert product.price() == pytest.approx(product_price)

# ---------------------------------------------------------
# 4. GIỎ HÀNG - B1.4

@pytest.mark.ui
def test_cart_line_price_equals_unit_price_times_quantity(page):
    """Goal: verify cart price calculations.
    Precondition: cart is empty and product is in stock.
    Expected: line price equals unit price times quantity and total is correct."""
    product = HomePage(page).open().open_product("Hammer")

    unit = product.price()

    product.add_to_cart(quantity=2)

    expect(product.cart_quantity).to_have_text("2")

    cart = product.go_to_cart()

    expect(cart.product_titles).to_have_count(1)

    assert cart.line_totals() == [
        pytest.approx(unit * 2)
    ]

    assert cart.total_value() == pytest.approx(
        sum(cart.line_totals())
    )


# ---------------------------------------------------------
# 5. GIỎ HÀNG - B1.6

@pytest.mark.ui
def test_cart_continue_shopping_returns_to_home(page):
    """Goal: verify continue shopping navigation.
    Precondition: none.
    Expected: clicking Continue Shopping returns to the product grid."""
    cart = (
        HomePage(page)
        .open()
        .open_product("Hammer")
        .add_to_cart()
        .go_to_cart()
    )

    expect(cart.product_titles.first).to_have_text("Hammer")

    cart.continue_shopping.click()

    expect(
        HomePage(page).product_names.first
    ).to_be_visible()


# ---------------------------------------------------------
# 6. XÁC THỰC - B1.5

@pytest.mark.ui
def test_login_empty_form_shows_required_errors(page):
    """Goal: verify required field validation.
    Precondition: none.
    Expected: email and password required errors are displayed."""
    login = LoginPage(page).open()

    login.submit_button.click()

    expect(login.email_error).to_contain_text(
        "Email is required"
    )

    expect(login.password_error).to_contain_text(
        "Password is required"
    )


# ---------------------------------------------------------
# 7. LIÊN HỆ, TÀI KHOẢN - B2.12

@pytest.mark.ui
def test_logged_in_page_shows_user_menu(logged_in_page):
    """Goal: verify a previously authenticated user can access the account.
    Precondition: authentication state is saved in auth_state.
    Expected: account page displays My account and QA Bot."""
    account = AccountPage(logged_in_page).open()

    expect(account.title).to_have_text("My account")

    expect(account.nav_menu).to_contain_text("QA Bot")

@pytest.mark.ui
def test_price_slider_filters_products(page):
    """Goal: verify maximum price slider.
    Precondition: product list is available.
    Expected: maximum price decreases by one and API receives the new price limit."""

    home = HomePage(page).open()

    # Get initial maximum price
    before = float(
        home.price_slider_max.get_attribute("aria-valuenow")
    )

    api_requests = []

    def record_request(request):
        if "api.practicesoftwaretesting.com/products" in request.url:
            api_requests.append(request)

    page.on("request", record_request)

    # Decrease maximum price by one
    home.decrease_max_price()

    after = float(
        home.price_slider_max.get_attribute("aria-valuenow")
    )

    # Verify slider value
    assert after == before - 1

    # Verify API request
    expect(home.product_names.first).to_be_visible()

    assert api_requests, "API products was not called"

    request = api_requests[-1]

    assert request.method == "QUERY"

    payload = request.post_data_json

    assert payload["between"] == f"price,1,{int(after)}"

    # Verify displayed product prices
    prices = home.prices()

    assert prices, "No products displayed after filtering"

    assert all(price <= after for price in prices), prices

@pytest.mark.ui
def test_contact_accepts_empty_attachment(page, tmp_path):
    """Goal: verify empty file attachment.
    Precondition: contact form is filled with valid information.
    Expected: empty attachment is accepted and form submission succeeds."""
    empty_file = tmp_path / "empty.txt"
    empty_file.write_bytes(b"")

    contact = ContactPage(page).open()

    contact.fill_form(
        first="QA",
        last="Tester",
        email="qa.tester@example.com",
        subject="Customer service",
        message="I am testing the empty file attachment feature."
    )

    contact.attach(empty_file)
    contact.submit()

    expect(contact.success).to_be_visible()

@pytest.mark.ui
def test_contact_rejects_non_empty_attachment(page, tmp_path):
    """Goal: verify non-empty file rejection.
    Precondition: contact form is filled with valid information.
    Expected: file containing data is rejected."""
    non_empty_file = tmp_path / "non_empty.txt"
    non_empty_file.write_text(
        "This file should be rejected.",
        encoding="utf-8"
    )

    contact = ContactPage(page).open()

    contact.fill_form(
        first="QA",
        last="Tester",
        email="qa.tester@example.com",
        subject=None,
        message="I am testing the non-empty file attachment feature."
    )

    contact.attach(non_empty_file)
    contact.submit()

    expect(contact.errors.first).to_be_visible()

@pytest.mark.ui
def test_footer_github_link_opens_new_tab(page):
    """Goal: verify GitHub footer link opens a new tab.
    Precondition: home page is available.
    Expected: a new tab navigates to GitHub."""
    home = HomePage(page).open()

    with page.context.expect_page() as page_info:
        home.open_github()

    github_page = page_info.value

    expect(github_page).to_have_url(
        re.compile(r"https://github\.com/")
    )

    github_page.close()