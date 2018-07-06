from flask_admin.contrib.sqla import ModelView
from flask import Blueprint

from flaskshop.extensions import admin_manager, db
from flaskshop.product.models import Product, ProductSku
from flaskshop.order.models import Order
from flaskshop.user.models import UserAddress

blueprint = Blueprint('admin_pannel', __name__, url_prefix='/admin', static_folder='../static')


class CustomView(ModelView):
    list_template = 'admin/list.html'
    create_template = 'admin/create.html'
    edit_template = 'admin/edit.html'
    can_delete = True
    can_export = True
    can_set_page_size = True


class ProductView(CustomView):
    column_list = ('id', 'title', 'image', 'on_sale', 'rating', 'sold_count', 'review_count', 'price')
    # column_filters = ('id', 'title') //TODO
    inline_models = (ProductSku,)


class UserAddressView(CustomView):
    can_delete = False


admin_manager.add_view(
    ProductView(Product, db.session, endpoint='Product_admin', menu_icon_type='fa',
                menu_icon_value='fa-bandcamp nav-icon'))
admin_manager.add_view(ModelView(Order, db.session, endpoint='Order_admin', menu_icon_type='fa',
                                 menu_icon_value='fa-cart-arrow-down nav-icon'))
admin_manager.add_view(UserAddressView(UserAddress, db.session, endpoint='User_address_admin', menu_icon_type='fa',
                                       menu_icon_value='fa-cart-arrow-down nav-icon'))
