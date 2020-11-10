def test_request(client):
    response = client.get('/products/example_id', follow_redirects=True)
    assert response.mimetype == 'text/html'
    assert response.data.decode() == '<div>example</div>'
