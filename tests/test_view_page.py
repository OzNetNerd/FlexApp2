import pytest
from flask_login import current_user

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def response(client):
    with client:
        client.post("/auth/login", data={"email": "newadmin@example.com", "password": "password"}, follow_redirects=True)
        return client.get('/companies/1', follow_redirects=True)

def test_status_code_ok(response):
    assert response.status_code == 200

def test_title_present(response):
    assert "<title>Viewing</title>" in response.data.decode()

def test_navbar_brand(response):
    assert "CRM Dashboard" in response.data.decode()

def test_tabs_exist(response):
    html = response.data.decode()
    assert 'id="tab-about-tab"' in html
    assert 'id="tab-insights-tab"' in html

def test_company_details_section_present(response):
    assert "Company Details" in response.data.decode()

def test_crisp_score_section_present(response):
    assert "CRISP Score" in response.data.decode()

def test_buttons_present(response):
    html = response.data.decode()
    for button in ['Add', 'Edit', 'Delete', 'Back']:
        assert button in html

def test_user_avatar_present(client):
    with client:
        client.post("/auth/login", data={"email": "newadmin@example.com", "password": "password"}, follow_redirects=True)
        client.get("/companies/1")
        assert current_user.is_authenticated
        assert current_user.name == "Test Admin"

def test_field_name_label_present(response):
    assert '<span class="fw-bold">Name</span>' in response.data.decode()

def test_field_description_label_present(response):
    assert '<span class="fw-bold">Description</span>' in response.data.decode()

def test_field_crisp_label_present(response):
    assert '<span class="fw-bold">CRISP</span>' in response.data.decode()
