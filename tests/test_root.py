import pytest


@pytest.mark.respx(base_url="https://www.reciperadar.com", assert_all_called=True)
def test_request(client, respx_mock):
    respx_mock.get("/api/recipes/explore").respond(
        json={
            "facets": {
                "products": [
                    {"key": "few_results", "count": 5},
                    {"key": "many_results", "count": 50},
                ]
            },
            "total": 0,
        }
    )
    response = client.get("/product-combinations/data.json")

    expected_link = "/product-combinations/+/many_results/data.json"
    assert response.mimetype == "application/json"
    assert expected_link in response.json["product-combinations"]
