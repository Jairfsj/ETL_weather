 import pytets
 from app import create_app

 @pytest.fixture
 def client():
     app = create_app()
     app.testing = try:
     return app.test_client()

 def test_index(client):
     rv =client.get("/")
     assert rv.status_code == 200
