from flask_admin.contrib.sqla import ModelView
from flask_admin.form import rules, fields
from flask import Blueprint
from jinja2 import Markup
from wtforms.fields import (
    IntegerField,
    BooleanField,
    DecimalField,
    TextAreaField,
    PasswordField,
    TextField,
)
from wtforms.widgets import TextArea

from flaskshop.extensions import admin_manager, db
from flaskshop.product.models import Product, ProductSku
from flaskshop.order.models import Order, OrderItem
from flaskshop.user.models import User
from flaskshop.cart.models import CouponCode

blueprint = Blueprint(
    "admin_pannel", __name__, url_prefix="/admin", static_folder="../static"
)


class CKTextAreaWidget(TextArea):
    def __call__(self, field, **kwargs):
        if kwargs.get("class"):
            kwargs["class"] += " ckeditor"
        else:
            kwargs.setdefault("class", "ckeditor")
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)


class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()


class CustomView(ModelView):
    list_template = "admin/list.html"
    create_template = "admin/create.html"
    edit_template = "admin/edit.html"
    can_delete = True
    can_export = True
    can_set_page_size = True


class ProductView(CustomView):
    column_list = (
        "id",
        "title",
        "image",
        "on_sale",
        "rating",
        "sold_count",
        "review_count",
        "price",
    )
    column_sortable_list = (
        "id",
        "title",
        "rating",
        "sold_count",
        "review_count",
        "price",
    )
    product_sku_options = {
        "form_excluded_columns": ("created_at",),
        "form_overrides": dict(description=TextField),
    }
    inline_models = [(ProductSku, product_sku_options)]
    form_excluded_columns = ("liked_users",)
    extra_js = ["//cdn.ckeditor.com/4.6.0/standard/ckeditor.js"]

    # column_editable_list = ('title', 'rating') //TODO
    # column_filters = ('id', 'title') //TODO

    def __init__(self):
        super().__init__(
            Product,
            db.session,
            endpoint="Product_admin",
            menu_icon_type="fa",
            menu_icon_value="fa-bandcamp nav-icon",
        )

    def _format_price(view, context, model, name):
        return Markup("￥{}".format(model.price))

    def _list_thumbnail(view, context, model, name):
        return Markup("<img src={} width=200 height=100/>".format(model.image))

    column_formatters = {"price": _format_price, "image": _list_thumbnail}

    form_extra_fields = {
        "on_sale": BooleanField(),
        "sold_count": IntegerField(),
        "review_count": IntegerField(),
        "rating": DecimalField(),
        "price": DecimalField(),
    }

    form_overrides = {"description": CKTextAreaField}


class OrderView(CustomView):
    can_create = False
    column_list = ("id", "no", "user", "total_amount", "paid_at")
    inline_models = (OrderItem,)
    form_excluded_columns = ("user",)

    def __init__(self):
        super().__init__(
            Order,
            db.session,
            endpoint="Order_admin",
            menu_icon_type="fa",
            menu_icon_value="fa-cart-arrow-down nav-icon",
        )

    def _format_price(view, context, model, name):
        return Markup("￥{}".format(model.total_amount))   

    column_formatters = {"total_amount": _format_price}


class CouponView(CustomView):
    column_list = (
        "id",
        "title",
        "type",
        "enabled",
        "value",
        "min_amount",
        "used_total",
    )
    form_excluded_columns = ("order",)

    def __init__(self):
        super().__init__(
            CouponCode,
            db.session,
            endpoint="Coupon_admin",
            menu_icon_type="fa",
            menu_icon_value="fa-bitcoin nav-icon",
        )

    def _format_used_total(view, context, model, name):
        return Markup("{}/{}".format(model.used, model.total))

    column_formatters = {"used_total": _format_used_total}


class UserView(CustomView):
    column_list = ("id", "username", "email", "active", "is_admin")
    form_excluded_columns = ("orders", "favor_products", "addresses", "cart_items")
    form_overrides = {"password": PasswordField}

    def __init__(self):
        super().__init__(
            User,
            db.session,
            endpoint="User_admin",
            menu_icon_type="fa",
            menu_icon_value="fa-user nav-icon",
        )


admin_manager.add_view(ProductView())
admin_manager.add_view(OrderView())
admin_manager.add_view(CouponView())
admin_manager.add_view(UserView())
