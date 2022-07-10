import json
from pathlib import Path
from tenacity import retry, wait_exponential

from flask import Flask, jsonify
from flask_frozen import Freezer
import httpx


USER_AGENT = "RecipeRadarContentCrawler 1.0.0"


content_directory = Path(__file__).parent.parent.joinpath("public").resolve()

app = Flask(__name__)
app.config.update({"FREEZER_DESTINATION": content_directory})

freezer = Freezer(app)

url_queue = []


def products_from_path(path):
    return path.split("/") if path else []


def product_combination_url(include, exclude):
    url = "/product-combinations"
    if include:
        url += "/+/"
        url += "/".join(include)
    if exclude:
        url += "/-/"
        url += "/".join(exclude)
    url += "/data.json"
    return url


def explore_params(include, exclude):
    return {"ingredients[]": include + [f"-{product}" for product in exclude]}


@retry(wait=wait_exponential(min=1, max=60))
def explore(params):
    return httpx.get(
        url="https://www.reciperadar.com/api/recipes/explore",
        headers={"User-Agent": USER_AGENT},
        params=params,
    ).json()


def render_content(include=None, exclude=None):
    include = include or []
    exclude = exclude or []
    depth = len(set(include + exclude))

    print(f"* Requesting include={include} exclude={exclude} ... ", end="")

    params = explore_params(include, exclude)
    response = explore(params)

    print(" done")

    products = []
    product_combinations = []
    recipes = []

    total = response["total"]
    choices = [
        product
        for product in response["facets"]["products"]
        if not depth > 2  # limit recursion depth
    ]
    for choice in choices:
        product, count = choice["key"], choice["count"]
        if count < 10:
            continue
        url = product_combination_url(include + [product], exclude)
        product_combinations.append(url)
        if include and count > total * 0.3:
            url = product_combination_url(include, exclude + [product])
            product_combinations.append(url)

    return {
        "products": products,
        "product-combinations": product_combinations,
        "recipes": recipes,
    }


@app.route("/product-combinations/data.json")
@app.route("/product-combinations/+/<path:include>/data.json")
@app.route("/product-combinations/+/<path:include>/-/<path:exclude>/data.json")
def product_combinations(include=None, exclude=None):
    include = products_from_path(include)
    exclude = products_from_path(exclude)
    content = render_content(include, exclude)
    if len(include) < 2:
        # set noindex response header
        pass
    return jsonify(content)


@freezer.register_generator
def product_combination_generator():
    yield product_combinations.__name__, {}
    yield from url_queue


def extract_links(content):
    if isinstance(content, dict):
        for key, value in content.items():
            yield from extract_links(value)
        return
    if isinstance(content, list):
        for item in content:
            yield from extract_links(item)
        return
    yield content


if __name__ == "__main__":
    for url, path in freezer.freeze_yield():
        path = Path(content_directory, path)
        with open(path) as f:
            content = json.loads(f.read())
            url_queue += extract_links(content)
