import string
import random
import time

from flaskshop.database import (
    Column,
    Model,
    SurrogatePK,
    db,
    reference_col,
    relationship,
)


class UserCart(SurrogatePK, Model):
    """A cart of a user"""

    __tablename__ = "cart_items"
    user_id = reference_col("users")
    user = relationship("User", backref="cart_items")
    product_sku_id = reference_col("product_skus")
    product_sku = relationship("ProductSku")
    amount = Column(db.Integer())

    def __repr__(self):
        return f"<Cart({self.id})>"

    def release(self, amount):
        """when submit order, release cart items in order"""
        self.amount -= amount
        if self.amount <= 0:
            self.delete()


class CouponCode(SurrogatePK, Model):
    """A promo code for an order"""

    __tablename__ = "coupon_codes"
    title = Column(db.String(255), nullable=False)
    code = Column(db.String(255), unique=True, nullable=False)
    type = Column(db.String(255), nullable=False)
    value = Column(db.String(255), nullable=False)
    total = Column(db.Integer())
    used = Column(db.Integer(), default=0)
    min_amount = Column(db.DECIMAL(10, 2))
    not_before = Column(db.DateTime())
    not_after = Column(db.DateTime())
    enabled = Column(db.Boolean(), default=True)

    @classmethod
    def generate_code(cls):
        code = ''.join(random.choices(string.ascii_uppercase, k=16))
        exist = cls.query.filter_by(code=code).first()
        if not exist:
            return code
        else:
            return cls.generate_code()

    def check_available(self, order_total_amount=None):
        if not self.enabled:
            raise Exception('This code can not use by system')
        if self.total - self.used < 0:
            raise Exception('The coupon has been redeemed')
        if self.not_before and self.not_before > time.time():
            raise Exception('The coupon can not use now, please retry later')
        if self.not_after and self.not_after < time.time():
            raise Exception('该优惠券已过期')
        if order_total_amount and order_total_amount < self.min_amount:
            raise Exception('订单金额不满足该优惠券最低金额')
        return True
