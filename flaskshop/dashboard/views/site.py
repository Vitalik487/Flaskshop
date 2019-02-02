from flask import render_template, redirect, url_for, request

from flaskshop.public.models import MenuItem, Page
from flaskshop.dashboard.models import DashboardMenu
from flaskshop.product.models import Category, Collection
from flaskshop.dashboard.forms import DashboardMenuForm, SiteMenuForm, SitePageForm


def site_menus():
    page = request.args.get("page", type=int, default=1)
    pagination = MenuItem.query.paginate(page, 10)
    props = {
        "id": "ID",
        "title": "Title",
        "order": "Order",
        "site_id": "Site Id",
        "parent_id": "Parent Id",
    }
    context = {
        "title": "Site Menus",
        "manage_endpoint": "dashboard.site_menus_manage",
        "items": pagination.items,
        "props": props,
        "pagination": pagination,
    }
    return render_template("dashboard/list.html", **context)


def site_menus_manage(id=None):
    if id:
        menu = MenuItem.get_by_id(id)
    else:
        menu = MenuItem()
    form = SiteMenuForm(obj=menu)
    if form.validate_on_submit():
        form.populate_obj(menu)
        menu.save()
        return redirect(url_for("dashboard.site_menus"))
    parents = MenuItem.first_level_items()
    categories = Category.query.all()
    collections = Collection.query.all()
    pages = Page.query.all()
    context = {
        "form": form,
        "parents": parents,
        "categories": categories,
        "collections": collections,
        "pages": pages,
    }
    return render_template("dashboard/site/site_menu.html", **context)


def dashboard_menus():
    dashboard_menus = DashboardMenu.query.all()
    props = {
        "id": "ID",
        "title": "Title",
        "order": "Order",
        "endpoint": "Endpoint",
        "icon_cls": "Icon class",
        "parent_id": "Parent Id",
    }
    context = {
        "title": "Dashboard Menus",
        "manage_endpoint": "dashboard.dashboard_menus_manage",
        "items": dashboard_menus,
        "props": props,
    }
    return render_template("dashboard/list.html", **context)


def dashboard_menus_manage(id=None):
    if id:
        menu = DashboardMenu.get_by_id(id)
    else:
        menu = DashboardMenu()
    form = DashboardMenuForm(obj=menu)
    if form.validate_on_submit():
        form.populate_obj(menu)
        menu.save()
        return redirect(url_for("dashboard.dashboard_menus"))
    parents = DashboardMenu.first_level_items()
    return render_template(
        "dashboard/site/dashboard_menu.html", form=form, parents=parents
    )


def site_pages():
    pages = Page.query.all()
    props = {
        "id": "ID",
        "title": "Title",
        "slug": "Slug",
        "url": "Url",
        "is_visible": "Is Visiable",
    }
    context = {
        "title": "Site Pages",
        "manage_endpoint": "dashboard.site_pages_manage",
        "items": pages,
        "props": props,
    }
    return render_template("dashboard/list.html", **context)


def site_pages_manage(id=None):
    if id:
        page = Page.get_by_id(id)
    else:
        page = Page()
    form = SitePageForm(obj=page)
    if form.validate_on_submit():
        form.populate_obj(page)
        page.save()
        return redirect(url_for("dashboard.site_pages"))
    return render_template("dashboard/site/site_page.html", form=form)
