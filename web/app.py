from flask import Flask, render_template
from flask_frozen import Freezer

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


@freezer.register_generator
def product_url_generator():
    yield product_view.__name__, {'product_id': 'example_id'}


if __name__ == '__main__':
    freezer.freeze()
