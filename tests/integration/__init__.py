"""Integration test layer: services + database with fresh in-memory SQLite per test.

Each test receives a complete isolated SQLite database with all tables created,
foreign keys enabled, and core lookup data (roles) pre-seeded. The `integration_db`
fixture (defined in conftest.py) patches all service modules' SessionLocal to use
this test database automatically.

Test files:
    test_auth_flow.py       Register → Login → Availability checks
    test_album_flow.py      Album CRUD → Ownership rules → Rename/Delete
    test_photo_flow.py      Photo upload → Cloudinary mock → Like state

Each test is fully isolated — no cross-test contamination, no real DB touched.

Run:
    pytest tests/integration/ -v
"""
