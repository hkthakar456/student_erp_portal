def test_student_submit_feedback(student_client):
    with student_client.session_transaction() as sess:
        token = sess["_csrf_token"]

    response = student_client.post("/feedback/", data={
        "csrf_token": token,
        "category": "Academics",
        "message": "Can we extend library reservation hours for study rooms?",
        "contact_email": "alex.rivers@campus.edu"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Your feedback has been submitted" in response.data

def test_admin_feedback_queue(admin_client):
    response = admin_client.get("/feedback/admin")
    assert response.status_code == 200
    assert b"Student Feedback Management Queue" in response.data
    assert b"Facilities" in response.data

def test_student_cannot_access_feedback_queue(student_client):
    response = student_client.get("/feedback/admin", follow_redirects=True)
    assert response.status_code == 200
    assert b"Access denied. Administrator privileges are required" in response.data

def test_admin_update_feedback_status(admin_client):
    with admin_client.session_transaction() as sess:
        token = sess["_csrf_token"]

    response = admin_client.post("/feedback/1/status", data={
        "csrf_token": token,
        "status": "In Progress",
        "admin_response": "IT dispatch unit has tested the access points."
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"status updated to" in response.data
    assert b"In Progress" in response.data
