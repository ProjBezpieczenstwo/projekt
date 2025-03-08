def test_404_error(test_client):
    response = test_client.get('/non-existent-endpoint')
    assert response.status_code == 404
    assert response.json['error'] == 'Page not found'
