def test_course_list(admin_client):
    response = admin_client.get("/courses/")
    assert response.status_code == 200
    assert b"Course Catalog" in response.data
    assert b"CS101" in response.data
    assert b"CS201" in response.data

def test_course_detail(admin_client):
    response = admin_client.get("/courses/1")
    assert response.status_code == 200
    assert b"CS101" in response.data
    assert b"Dr. Sarah Mitchell" in response.data

def test_create_course(admin_client):
    with admin_client.session_transaction() as sess:
        token = sess["_csrf_token"]

    response = admin_client.post("/courses/new", data={
        "csrf_token": token,
        "code": "CYBER101",
        "title": "Introduction to Cybersecurity",
        "instructor": "Prof. Ada Lovelace",
        "credits": 3,
        "capacity": 30,
        "term": "Fall 2026",
        "department": "Computer Science",
        "description": "Network defense and cryptographic principles."
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"CYBER101" in response.data
    assert b"Introduction to Cybersecurity" in response.data

def test_prevent_duplicate_active_enrollment(admin_client):
    with admin_client.session_transaction() as sess:
        token = sess["_csrf_token"]

    # In seed data, Student 1 (Alex) is already enrolled in Course 2 (CS201)
    response = admin_client.post("/students/1/enroll", data={
        "csrf_token": token,
        "course_id": 2
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"already actively enrolled" in response.data

def test_enroll_and_withdraw(admin_client):
    with admin_client.session_transaction() as sess:
        token = sess["_csrf_token"]

    # Student 4 (Elena) is only in CS101. Enroll her in CS201
    response = admin_client.post("/students/4/enroll", data={
        "csrf_token": token,
        "course_id": 2
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"successfully enrolled" in response.data

    # Now withdraw her
    # Elena's enrollment ID for CS201
    with admin_client.application.app_context():
        enrollments = admin_client.application.repository.get_enrollments_for_student(4)
        cs201_enr = next(e for e in enrollments if e["code"] == "CS201")
        enr_id = cs201_enr["enrollment_id"]

    withdraw_res = admin_client.post(f"/students/4/withdraw/{enr_id}", data={
        "csrf_token": token
    }, follow_redirects=True)
    assert withdraw_res.status_code == 200
    assert b"Course enrollment withdrawn" in withdraw_res.data
