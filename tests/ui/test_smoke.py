
import pytest
from playwright.sync_api import expect

from pages.home_page import HomePage
from pages.product_page import ProductPage
from pages.login_page import LoginPage
from pages.contact_page import ContactPage
import re


@pytest.mark.smoke
def test_search_pliers(page):
    """
    Mục tiêu: Kiểm tra chức năng tìm kiếm sản phẩm pliers.
    Điều kiện: Người dùng mở trang chủ và nhập từ khóa pliers.
    Kết quả mong đợi: Tất cả tên sản phẩm hiển thị đều chứa pliers.
    """

    home_page = HomePage(page)

    # Mở trang chủ
    home_page.open()

    # Tìm kiếm sản phẩm
    home_page.search("pliers")

    # Chờ tìm kiếm hoàn tất
    expect(home_page.search_completed).to_be_visible()

    # Lấy danh sách tên sản phẩm
    product_names = home_page.product_names.all_inner_texts()

    # Kiểm tra có sản phẩm
    assert len(product_names) > 0, "Không tìm thấy sản phẩm!"

    # Kiểm tra tất cả sản phẩm đều chứa pliers
    for name in product_names:
        assert "pliers" in name.lower(), (
            f"Sản phẩm không chứa từ khóa pliers: {name}"
        )


@pytest.mark.smoke
def test_add_product_to_cart(page):
    """
    Mục tiêu: Kiểm tra chức năng thêm sản phẩm vào giỏ hàng.
    Điều kiện: Người dùng mở sản phẩm Claw Hammer.
    Kết quả mong đợi: Badge giỏ hàng hiển thị số lượng 3.
    """

    home_page = HomePage(page)

    # Mở trang chủ
    home_page.open()

    # Tìm kiếm sản phẩm Claw Hammer
    home_page.search("Claw Hammer")

    # Mở chính xác sản phẩm Claw Hammer
    product_page = home_page.open_product("Claw Hammer")

    # Thêm sản phẩm với số lượng 3
    product_page.add_to_cart(3)

    # Kiểm tra badge giỏ hàng hiển thị 3
    expect(product_page.cart_quantity).to_have_text("3")


@pytest.mark.smoke
def test_login_invalid_email(page):
    """
    Mục tiêu: Kiểm tra chức năng đăng nhập với email không tồn tại.
    Điều kiện: Người dùng nhập email không tồn tại và mật khẩu bất kỳ.
    Kết quả mong đợi: Hiện Invalid email or password, URL vẫn kết thúc bằng /auth/login.
    """

    login_page = LoginPage(page)

    # Mở trang đăng nhập
    login_page.open()

    # Nhập email không tồn tại và mật khẩu bất kỳ
    login_page.login(
        "nonexistent.20261110@example.com",
        "AnyPassword123!"
    )

    # Kiểm tra thông báo lỗi
    expect(login_page.error).to_contain_text(
        "Invalid email or password"
    )

    # Kiểm tra URL vẫn ở trang đăng nhập
    expect(page).to_have_url(
        re.compile(r"/auth/login$")
    )


@pytest.mark.smoke
def test_contact_form_empty(page):
    """
    Mục tiêu: Kiểm tra validation khi gửi form Contact trống.
    Điều kiện: Người dùng mở trang Contact và không nhập thông tin.
    Kết quả mong đợi: Hiện Subject is required và Message is required.
    """

    contact_page = ContactPage(page)

    # Mở trang Contact
    contact_page.open()

    # Nhấn Send khi form đang trống
    contact_page.submit()


    # Kiểm tra lỗi Subject
    expect(contact_page.subject_error).to_be_visible()
    expect(contact_page.subject_error).to_contain_text(
        "Subject is required"
    )

    # Kiểm tra lỗi Message
    expect(contact_page.message_error).to_be_visible()
    expect(contact_page.message_error).to_contain_text(
        "Message is required"
    )

