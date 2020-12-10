import json
import responses


@responses.activate
def test_request(client):
    responses.add(
        method=responses.GET,
        url='https://www.reciperadar.com/api/recipes/explore',
        body=json.dumps({
            'facets': {
                'products': [
                    {'key': 'few_results', 'count': 5},
                    {'key': 'many_results', 'count': 50},
                ]
            },
            'total': 0
        })
    )
    response = client.get('/product-combinations/data.json')

    expected_link = '/product-combinations/+/many_results/data.json'
    assert response.mimetype == 'application/json'
    assert expected_link in response.json['product-combinations']
