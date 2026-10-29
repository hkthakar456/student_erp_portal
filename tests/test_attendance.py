def test_attendance_list(admin_client):
    response = admin_client.get("/attendance/")
    assert response.status_code == 200
    assert b"Class Attendance Tracking" in response.data
    assert b"Alex Rivers" in response.data

def test_record_attendance_success(admin_client):
    with admin_client.session_transaction() as sess:
        token = sess["_csrf_token"]

    response = admin_client.post("/attendance/record", data={
        "csrf_token": token,
        "student_id": 2, # Sophia
        "course_id": 1,  # CS101
        "date": "2026-10-25",
        "status": "Present",
        "remarks": "Participated in lab exercise"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Attendance record saved successfully" in response.data

def test_attendance_summary_calculation(student_client):
    # Alex Rivers has attendance recorded in seed
    response = student_client.get("/attendance/")
    assert response.status_code == 200
    assert b"Calculated Rate" in response.data
    assert b"Present Sessions" in response.data
