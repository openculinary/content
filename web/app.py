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


def spider_combinations(ingredients=None):
    ingredients = ingredients or []
    depth = len(ingredients)

    if depth >= 3:
        return

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
        yield from spider_combinations(ingredients + [product])
        if count > total * 0.3:
            exclude_product = f'-{product}'
            yield from spider_combinations(ingredients + [exclude_product])
    if depth >= 2:
        yield ingredients


@freezer.register_generator
def product_url_generator():
    yield product_view.__name__, {'product_id': 'example_id'}


@freezer.register_generator
def product_combination_generator():
    for ingredients in spider_combinations():
        include = [i for i in ingredients if not i.startswith('-')]
        if include:
            params = {'include': '/'.join(include)}
            yield product_combination_view.__name__, params

        exclude = [i for i in ingredients if i.startswith('-')]
        if include and exclude:
            params = {'include': '/'.join(include), 'exclude': '/'.join(exclude)}
            yield product_combination_with_exclusions_view.__name__, params


if __name__ == '__main__':
    freezer.freeze()
