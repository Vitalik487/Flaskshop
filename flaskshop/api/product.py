from flask_restplus import Namespace, Resource, fields
from flask import request

from flaskshop.product.models import Product
from flaskshop.product.utils import add_to_currentuser_cart

api = Namespace('products', description='Products related operations')
parser = api.parser()
parser.add_argument('variant_id', type=int, required=True, help='The variant')
parser.add_argument('quantity', type=int, required=True, help='The quantity')

product_list = api.model('ProductList', {
    'id': fields.String(required=True, description='The product identifier'),
    'title': fields.String(required=True, description='The product name'),
    'description': fields.String(description='The product description'),
    'price': fields.String(description='The product price'),
    'first_img': fields.String(description='The product first img', attribute='get_first_img'),
})
variant = api.model('Variant', {
    'id': fields.String(required=True, description='The variant identifier'),
    'sku': fields.String(required=True, description='The variant sku'),
    'title': fields.String(required=True, description='The variant name'),
    'price': fields.String(required=True, description='The variant price'),
})
product_detail = api.model('ProductDetail', {
    'id': fields.String(required=True, description='The product identifier'),
    'title': fields.String(required=True, description='The product name'),
    'description': fields.String(description='The product description'),
    'price': fields.String(description='The product price'),
    'images': fields.List(fields.String, description='The product images'),
    'variant': fields.List(fields.Nested(variant), description='The product variant')
})


@api.route('/')
class ProductList(Resource):
    @api.doc('list_products')
    @api.marshal_list_with(product_list)
    def get(self):
        """List all products"""
        page = request.args.get('page', 1, int)
        products = Product.query.paginate(page, per_page=8).items
        return products


@api.route('/<id>')
@api.param('id', 'The product identifier')
@api.response(404, 'Product not found')
class ProductDetail(Resource):
    @api.doc('get_product')
    @api.marshal_with(product_detail)
    def get(self, id):
        """Fetch a product """
        product = Product.query.get(id)
        if product:
            return product
        api.abort(404)

    @api.doc(parser=parser)
    def post(self, id):
        """post product to current user cart"""
        args = parser.parse_args()
        add_to_currentuser_cart(args['quantity'], args['variant_id'])
        return '', 201
