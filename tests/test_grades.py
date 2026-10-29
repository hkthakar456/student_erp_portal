def test_grade_book_renders(admin_client):
    response = admin_client.get("/grades/")
    assert response.status_code == 200
    assert b"Academic Grade Book" in response.data
    assert b"educational simulation" in response.data

def test_record_grade_valid(admin_client):
    with admin_client.session_transaction() as sess:
        token = sess["_csrf_token"]

    response = admin_client.post("/grades/record", data={
        "csrf_token": token,
        "student_id": 1,
        "course_id": 2,
        "assessment_name": "Quiz 2: Binary Search Trees",
        "score": 18.5,
        "max_score": 20.0,
        "weight_percentage": 5.0,
        "remarks": "Solid complexity proof"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"recorded successfully" in response.data

def test_record_grade_score_exceeding_max_rejected(admin_client):
    with admin_client.session_transaction() as sess:
        token = sess["_csrf_token"]

    response = admin_client.post("/grades/record", data={
        "csrf_token": token,
        "student_id": 1,
        "course_id": 2,
        "assessment_name": "Invalid Score Test",
        "score": 105.0,
        "max_score": 100.0,
        "weight_percentage": 10.0,
        "remarks": "Should be rejected"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"cannot be negative or exceed the maximum score" in response.data
