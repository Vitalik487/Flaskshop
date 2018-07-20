# -*- coding: utf-8 -*-
"""Click commands."""
import os
from glob import glob
from subprocess import call

import click
import random
from flask import current_app
from flask.cli import with_appcontext
from werkzeug.exceptions import MethodNotAllowed, NotFound
from faker import Faker

from flaskshop.database import db
from flaskshop.product.models import Product, ProductSku
from flaskshop.checkout.models import CouponCode
from flaskshop.constant import TYPE_FIXED, TYPE_PERCENT

HERE = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.join(HERE, os.pardir)
TEST_PATH = os.path.join(PROJECT_ROOT, "tests")


@click.command()
def test():
    """Run the tests."""
    import pytest

    rv = pytest.main([TEST_PATH, "--verbose"])
    exit(rv)


@click.command()
@click.option(
    "-f",
    "--fix-imports",
    default=False,
    is_flag=True,
    help="Fix imports using isort, before linting",
)
def lint(fix_imports):
    """Lint and check code style with flake8 and isort."""
    skip = ["node_modules", "requirements"]
    root_files = glob("*.py")
    root_directories = [
        name for name in next(os.walk("."))[1] if not name.startswith(".")
    ]
    files_and_directories = [
        arg for arg in root_files + root_directories if arg not in skip
    ]

    def execute_tool(description, *args):
        """Execute a checking tool with its arguments."""
        command_line = list(args) + files_and_directories
        click.echo("{}: {}".format(description, " ".join(command_line)))
        rv = call(command_line)
        if rv != 0:
            exit(rv)

    if fix_imports:
        execute_tool("Fixing import order", "isort", "-rc")
    execute_tool("Checking code style", "flake8")


@click.command()
def clean():
    """Remove *.pyc and *.pyo files recursively starting at current directory.

    Borrowed from Flask-Script, converted to use Click.
    """
    for dirpath, dirnames, filenames in os.walk("."):
        for filename in filenames:
            if filename.endswith(".pyc") or filename.endswith(".pyo"):
                full_pathname = os.path.join(dirpath, filename)
                click.echo("Removing {}".format(full_pathname))
                os.remove(full_pathname)


@click.command()
@click.option("--url", default=None, help="Url to test (ex. /static/image.png)")
@click.option(
    "--order", default="rule", help="Property on Rule to order by (default: rule)"
)
@with_appcontext
def urls(url, order):
    """Display all of the url matching routes for the project.

    Borrowed from Flask-Script, converted to use Click.
    """
    rows = []
    column_length = 0
    column_headers = ("Rule", "Endpoint", "Arguments")

    if url:
        try:
            rule, arguments = current_app.url_map.bind("localhost").match(
                url, return_rule=True
            )
            rows.append((rule.rule, rule.endpoint, arguments))
            column_length = 3
        except (NotFound, MethodNotAllowed) as e:
            rows.append(("<{}>".format(e), None, None))
            column_length = 1
    else:
        rules = sorted(
            current_app.url_map.iter_rules(), key=lambda rule: getattr(rule, order)
        )
        for rule in rules:
            rows.append((rule.rule, rule.endpoint, None))
        column_length = 2

    str_template = ""
    table_width = 0

    if column_length >= 1:
        max_rule_length = max(len(r[0]) for r in rows)
        max_rule_length = max_rule_length if max_rule_length > 4 else 4
        str_template += "{:" + str(max_rule_length) + "}"
        table_width += max_rule_length

    if column_length >= 2:
        max_endpoint_length = max(len(str(r[1])) for r in rows)
        # max_endpoint_length = max(rows, key=len)
        max_endpoint_length = max_endpoint_length if max_endpoint_length > 8 else 8
        str_template += "  {:" + str(max_endpoint_length) + "}"
        table_width += 2 + max_endpoint_length

    if column_length >= 3:
        max_arguments_length = max(len(str(r[2])) for r in rows)
        max_arguments_length = max_arguments_length if max_arguments_length > 9 else 9
        str_template += "  {:" + str(max_arguments_length) + "}"
        table_width += 2 + max_arguments_length

    click.echo(str_template.format(*column_headers[:column_length]))
    click.echo("-" * table_width)

    for row in rows:
        click.echo(str_template.format(*row[:column_length]))


@click.command()
@click.option("--type", default='product', help="which type to seed: product or coupon")
@click.option("--num", default=60, help="how many to seed")
@with_appcontext
def seed(type, num):
    fake = Faker()

    if type == 'product':
        img_list = [
            "https://lccdn.phphub.org/uploads/images/201806/01/5320/7kG1HekGK6.jpg",
            "https://lccdn.phphub.org/uploads/images/201806/01/5320/1B3n0ATKrn.jpg",
            "https://lccdn.phphub.org/uploads/images/201806/01/5320/r3BNRe4zXG.jpg",
            "https://lccdn.phphub.org/uploads/images/201806/01/5320/C0bVuKB2nt.jpg",
            "https://lccdn.phphub.org/uploads/images/201806/01/5320/82Wf2sg8gM.jpg",
            "https://lccdn.phphub.org/uploads/images/201806/01/5320/nIvBAQO5Pj.jpg",
            "https://lccdn.phphub.org/uploads/images/201806/01/5320/XrtIwzrxj7.jpg",
            "https://lccdn.phphub.org/uploads/images/201806/01/5320/uYEHCJ1oRp.jpg",
            "https://lccdn.phphub.org/uploads/images/201806/01/5320/2JMRaFwRpo.jpg",
            "https://lccdn.phphub.org/uploads/images/201806/01/5320/pa7DrV43Mw.jpg",
        ]

        for i in range(num):
            product = Product(
                title=fake.word(),
                description=fake.text(),
                image=random.choice(img_list),
                rating=random.randint(0, 5),
                sold_count=random.randint(100, 500),
                review_count=random.randint(10, 300),
                price=round(random.uniform(1, 5000), 2),
            )
            product_sku1 = ProductSku(
                title=fake.word(),
                description=fake.sentence(),
                price=round(random.uniform(1, 5000), 2),
                stock=random.randint(10, 300),
            )
            product_sku2 = ProductSku(
                title=fake.word(),
                description=fake.sentence(),
                price=round(random.uniform(1, 5000), 2),
                stock=random.randint(10, 300),
            )
            product.sku = [product_sku1, product_sku2]
            db.session.add(product)

        db.session.commit()
    elif type == 'coupon':
        for i in range(num):
            type = random.choice([TYPE_FIXED, TYPE_PERCENT])
            value = random.randint(1, 200) if type == TYPE_FIXED else random.randint(1, 50)
            # 如果是固定金额，则最低订单金额必须要比优惠金额高 0.01 元
            if type == TYPE_FIXED:
                min_amount = value + 0.01
            else:
                # 如果是百分比折扣，有 50% 概率不需要最低订单金额
                if random.randint(0, 100) < 50:
                    min_amount = 0
                else:
                    min_amount = random.randint(100, 1000)
            coupon = CouponCode(
                title = fake.word(),
                code = CouponCode.generate_code(),
                type = type,
                value = value,
                total = 1000,
                min_amount = min_amount
            )
            db.session.add(coupon)
        db.session.commit()