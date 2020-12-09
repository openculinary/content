from flask import Flask, render_template
from flask_frozen import Freezer
import requests

app = Flask(__name__)
app.config.update({'FREEZER_DESTINATION': '../public'})

freezer = Freezer(app)


@app.route('/products/<product_id>/')
def product_view(product_id):
    product = {
        'id': product_id,
        'name': 'example',
    }
    return render_template('product.html', product=product)


def products_from_path(path):
    products = path.split('/')
    products = [{'singular': product} for product in products]
    return products


@app.route('/product-combinations/+/<path:include>/')
def product_combination_view(include):
    include = products_from_path(include)
    return render_template(
        'combination.html',
        include=include
    )


@app.route('/product-combinations/+/<path:include>/-/<path:exclude>/')
def product_combination_with_exclusions_view(include, exclude):
    include = products_from_path(include)
    exclude = products_from_path(exclude)
    return render_template(
        'combination.html',
        include=include,
        exclude=exclude
    )


def spider_combinations(include=None, exclude=None):
    include = include or []
    exclude = exclude or []
    depth = len(set(include + exclude))

    if depth > 3:
        return

    ingredients = include + [f'-{product}' for product in exclude]
    response = requests.get(
        url='https://www.reciperadar.com/api/recipes/explore',
        params={'ingredients[]': ingredients}
    ).json()

    total = response['total']
    choices = [product for product in response['facets']['products']]
    for choice in choices:
        product, count = choice['key'], choice['count']
        if count < 10:
            continue
        yield from spider_combinations(include + [product], exclude)
        if count > total * 0.3:
            yield from spider_combinations(include, exclude + [product])
    if len(include) >= 2:
        yield include, exclude


@freezer.register_generator
def product_url_generator():
    yield product_view.__name__, {'product_id': 'example_id'}


@freezer.register_generator
def product_combination_generator():
    for include, exclude in spider_combinations():
        params = {'include': '/'.join(include)}
        yield product_combination_view.__name__, params
        if exclude:
            params = {**params, **{'exclude': '/'.join(exclude)}}
            yield product_combination_with_exclusions_view.__name__, params


if __name__ == '__main__':
    freezer.freeze()
