from flask import request, render_template, redirect, url_for, current_app
from flaskshop.product.models import (
    ProductAttribute,
    ProductType,
    Collection,
    Product,
    Category,
)
from flaskshop.dashboard.forms import AttributeForm, CollectionForm, CategoryForm


def attributes():
    page = request.args.get("page", type=int, default=1)
    pagination = ProductAttribute.query.paginate(page, 10)
    props = {
        "id": "ID",
        "title": "Title",
        "values_label": "Value",
        "types_label": "ProductType",
    }
    context = {
        "title": "Product Attribute",
        "manage_endpoint": "dashboard.attribute_manage",
        "items": pagination.items,
        "props": props,
        "pagination": pagination,
    }
    return render_template("dashboard/list.html", **context)


def attribute_manage(id=None):
    if id:
        attr = ProductAttribute.get_by_id(id)
    else:
        attr = ProductAttribute()
    form = AttributeForm(obj=attr)
    if form.validate_on_submit():
        attr.title = form.title.data
        attr.update_types(form.types.data)
        attr.update_values(form.values.data)
        attr.save()
        return redirect(url_for("dashboard.attributes"))
    product_types = ProductType.query.all()
    return render_template(
        "dashboard/product/attribute.html", form=form, product_types=product_types
    )


def collections():
    page = request.args.get("page", type=int, default=1)
    pagination = Collection.query.paginate(page, 10)
    props = {"id": "ID", "title": "Title", "created_at": "Created At"}
    context = {
        "title": "Product Collection",
        "manage_endpoint": "dashboard.collection_manage",
        "items": pagination.items,
        "props": props,
        "pagination": pagination,
    }
    return render_template("dashboard/list.html", **context)


def collection_manage(id=None):
    if id:
        collection = Collection.get_by_id(id)
    else:
        collection = Collection()
    form = CollectionForm(obj=collection)
    if form.validate_on_submit():
        collection.title = form.title.data
        collection.update_products(form.products.data)
        image = form.bgimg_file.data
        background_img = image.filename
        upload_file = current_app.config["UPLOAD_DIR"] / background_img
        upload_file.write_bytes(image.read())
        collection.background_img = (
            current_app.config["UPLOAD_FOLDER"] + "/" + background_img
        )
        collection.save()
        return redirect(url_for("dashboard.collections"))
    products = Product.query.all()
    return render_template(
        "dashboard/product/collection.html", form=form, products=products
    )


def categories():
    page = request.args.get("page", type=int, default=1)
    pagination = Category.query.paginate(page, 10)
    props = {
        "id": "ID",
        "title": "Title",
        "parent": "Parent",
        "created_at": "Created At",
    }
    context = {
        "title": "Product Category",
        "manage_endpoint": "dashboard.category_manage",
        "items": pagination.items,
        "props": props,
        "pagination": pagination,
    }
    return render_template("dashboard/list.html", **context)


def category_manage(id=None):
    if id:
        category = Category.get_by_id(id)
    else:
        category = Category()
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        category.title = form.title.data
        category.parent_id = form.parents.data
        image = form.bgimg_file.data
        background_img = image.filename
        upload_file = current_app.config["UPLOAD_DIR"] / background_img
        upload_file.write_bytes(image.read())
        category.background_img = (
            current_app.config["UPLOAD_FOLDER"] + "/" + background_img
        )
        category.save()
        return redirect(url_for("dashboard.categories"))
    parents = Category.first_level_items()
    return render_template(
        "dashboard/product/category.html", form=form, parents=parents
    )
