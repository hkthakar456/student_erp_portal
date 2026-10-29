def test_login_page_renders(client):
    response = client.get("/auth/login")
    assert response.status_code == 200
    assert b"Beacon ERP" in response.data
    assert b"admin@campus.edu" in response.data

def test_login_success_admin(client):
    # Retrieve page to set up CSRF token in session
    client.get("/auth/login")
    with client.session_transaction() as sess:
        token = sess["_csrf_token"]

    response = client.post("/auth/login", data={
        "email": "admin@campus.edu",
        "password": "AdminPass123!",
        "csrf_token": token
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Welcome back!" in response.data
    with client.session_transaction() as sess:
        assert sess.get("role") == "admin"
        assert sess.get("logged_in") is True

def test_login_invalid_password(client):
    client.get("/auth/login")
    with client.session_transaction() as sess:
        token = sess["_csrf_token"]

    response = client.post("/auth/login", data={
        "email": "admin@campus.edu",
        "password": "WrongPassword!",
        "csrf_token": token
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Invalid email or password" in response.data

def test_login_csrf_protection(client):
    response = client.post("/auth/login", data={
        "email": "admin@campus.edu",
        "password": "AdminPass123!",
        "csrf_token": "tampered-token"
    }, follow_redirects=True)

    assert b"Security check failed" in response.data

def test_logout(admin_client):
    response = admin_client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"signed out successfully" in response.data
    with admin_client.session_transaction() as sess:
        assert sess.get("logged_in") is None

def test_unauthenticated_access_redirects(client):
    response = client.get("/")
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]

def test_student_cannot_access_admin_routes(student_client):
    response = student_client.get("/students/new", follow_redirects=True)
    assert response.status_code == 200
    assert b"Access denied. Administrator privileges are required" in response.data
