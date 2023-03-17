from datetime import datetime

from flask import redirect, render_template, request, url_for
from flask_babel import lazy_gettext

from flaskshop.constant import DiscountValueTypeKinds, VoucherTypeKinds
from flaskshop.dashboard.forms import SaleForm, VoucherForm
from flaskshop.discount.models import Sale, Voucher
from flaskshop.product.models import Category, Product


def vouchers():
    page = request.args.get("page", type=int, default=1)
    pagination = Voucher.query.paginate(page, 10)
    props = {
        "id": lazy_gettext("ID"),
        "title": lazy_gettext("Title"),
        "type_human": lazy_gettext("Type"),
        "usage_limit": lazy_gettext("Usage Limit"),
        "used": lazy_gettext("Used"),
        "discount_value_type_human": lazy_gettext("Discount Type"),
        "discount_value": lazy_gettext("Discount Value"),
    }
    context = {
        "title": lazy_gettext("Voucher"),
        "items": pagination.items,
        "props": props,
        "pagination": pagination,
        "identity": lazy_gettext("vouchers"),
    }
    return render_template("list.html", **context)


def vouchers_manage(id=None):
    if id:
        voucher = Voucher.get_by_id(id)
        form = VoucherForm(obj=voucher)
    else:
        form = VoucherForm()
    if form.validate_on_submit():
        if not id:
            voucher = Voucher()
        start_date, end_date = form.validity_period.data.split("-")
        voucher.start_date = datetime.strptime(start_date.strip(), "%m/%d/%Y")
        voucher.end_date = datetime.strptime(end_date.strip(), "%m/%d/%Y")
        del form.validity_period
        form.populate_obj(voucher)
        voucher.save()
        return redirect(url_for("dashboard.vouchers"))
    products = Product.query.all()
    categories = Category.query.all()
    voucher_types = [dict(id=kind.value, title=kind.name) for kind in VoucherTypeKinds]
    discount_types = [
        dict(id=kind.value, title=kind.name) for kind in DiscountValueTypeKinds
    ]
    context = {
        "form": form,
        "products": products,
        "categories": categories,
        "voucher_types": voucher_types,
        "discount_types": discount_types,
    }
    return render_template("discount/voucher.html", **context)


def sales():
    page = request.args.get("page", type=int, default=1)
    pagination = Sale.query.paginate(page, 10)
    props = {
        "id": lazy_gettext("ID"),
        "title": lazy_gettext("Title"),
        "discount_value_type_label": lazy_gettext("Discount Type"),
        "discount_value": lazy_gettext("Discount Value"),
    }
    context = {
        "title": lazy_gettext("Sale"),
        "items": pagination.items,
        "props": props,
        "pagination": pagination,
        "identity": lazy_gettext("sales"),
    }
    return render_template("list.html", **context)


def sales_manage(id=None):
    if id:
        sale = Sale.get_by_id(id)
        form = SaleForm(obj=sale)
    else:
        sale = Sale()
        form = SaleForm()

    form.products_ids.choices = [(p.id, p.title) for p in Product.query.all()]
    form.categories_ids.choices = [(c.id, c.title) for c in Category.query.all()]
    form.discount_value_type.choices = [(k.value, k.name) for k in DiscountValueTypeKinds]

    if form.validate_on_submit():
        sale.update_products(form.products_ids.data)
        sale.update_categories(form.categories_ids.data)
        del form.products_ids
        del form.categories_ids
        form.populate_obj(sale)
        sale.save()
        return redirect(url_for("dashboard.sales"))

    context = {
        "form": form
    }
    return render_template("discount/sale.html", **context)
