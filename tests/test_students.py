def test_student_list_authenticated(admin_client):
    response = admin_client.get("/students/")
    assert response.status_code == 200
    assert b"Student Directory" in response.data
    assert b"Alex Rivers" in response.data
    assert b"STU-2024-001" in response.data

def test_student_search_filtering(admin_client):
    response = admin_client.get("/students/?q=Sophia")
    assert response.status_code == 200
    assert b"Sophia Chen" in response.data
    assert b"Alex Rivers" not in response.data

def test_student_detail_view(admin_client):
    response = admin_client.get("/students/1")
    assert response.status_code == 200
    assert b"Alex Rivers" in response.data
    assert b"STU-2024-001" in response.data
    assert b"Computer Science (B.Sc.)" in response.data

def test_admin_create_student_success(admin_client):
    with admin_client.session_transaction() as sess:
        token = sess["_csrf_token"]

    response = admin_client.post("/students/new", data={
        "csrf_token": token,
        "student_id_code": "STU-2024-999",
        "first_name": "Oliver",
        "last_name": "Queen",
        "email": "oliver.queen@campus.edu",
        "phone": "+1 (555) 019-9999",
        "program": "Computer Science (B.Sc.)",
        "year_level": "Year 1 (Freshman)",
        "status": "Active",
        "gpa": "3.85",
        "date_of_birth": "2005-01-01",
        "address": "Starling Dorm 101"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Oliver Queen" in response.data
    assert b"STU-2024-999" in response.data

def test_admin_create_student_duplicate_id_code_rejected(admin_client):
    with admin_client.session_transaction() as sess:
        token = sess["_csrf_token"]

    # STU-2024-001 already exists
    response = admin_client.post("/students/new", data={
        "csrf_token": token,
        "student_id_code": "STU-2024-001",
        "first_name": "Duplicate",
        "last_name": "Test",
        "email": "unique.email@campus.edu",
        "program": "Computer Science (B.Sc.)",
        "year_level": "Year 1 (Freshman)",
        "status": "Active"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"is already assigned to another student" in response.data

def test_toggle_student_status(admin_client):
    with admin_client.session_transaction() as sess:
        token = sess["_csrf_token"]

    response = admin_client.post("/students/1/toggle-status", data={
        "csrf_token": token
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"status changed to Inactive" in response.data

def test_student_cannot_access_directory(student_client):
    response = student_client.get("/students/", follow_redirects=True)
    assert response.status_code == 200
    assert b"Access denied. Administrator privileges are required" in response.data

def test_student_can_view_own_profile(student_client):
    # Student 1 is Alex Rivers
    response = student_client.get("/students/1")
    assert response.status_code == 200
    assert b"Alex Rivers" in response.data
    assert b"STU-2024-001" in response.data

def test_student_cannot_view_other_student_profile(student_client):
    # Student 1 (Alex) attempting to view Student 2 (Sophia)
    response = student_client.get("/students/2", follow_redirects=True)
    assert response.status_code == 200
    assert b"Access denied. You can only view your own student profile" in response.data

def test_student_my_profile_shortcut(student_client):
    response = student_client.get("/students/profile", follow_redirects=True)
    assert response.status_code == 200
    assert b"Alex Rivers" in response.data
    assert b"STU-2024-001" in response.data
