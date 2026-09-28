import unittest

from flask import Flask
from sqlalchemy.pool import StaticPool

from user_management import UserAccount, db, register_user_management


class UserManagementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = Flask(__name__)
        cls.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
        cls.app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "poolclass": StaticPool,
            "connect_args": {"check_same_thread": False},
        }
        cls.app.config["TESTING"] = True
        cls.app.config["SECRET_KEY"] = "test-signing-key"
        db.init_app(cls.app)
        register_user_management(cls.app)
        with cls.app.app_context():
            UserAccount.__table__.create(db.engine, checkfirst=True)

    def setUp(self):
        with self.app.app_context():
            db.session.remove()
            db.session.query(UserAccount).delete()
            db.session.commit()
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()

    def test_owner_setup_and_user_role_access(self):
        response = self.client.get("/api/auth/session")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json["setup_required"])
        self.assertEqual(self.client.get("/api/departments").status_code, 401)

        response = self.client.post("/api/auth/setup", json={
            "username": "owner.test",
            "display_name": "Platform Owner",
            "password": "correct-horse-battery",
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["user"]["role"], "super_admin")

        response = self.client.post("/api/auth/users", json={
            "username": "viewer.test",
            "display_name": "Read Only",
            "password": "another-long-password",
            "role": "viewer",
        })
        self.assertEqual(response.status_code, 201)
        self.assertNotIn("password_hash", response.json)

        response = self.client.post("/api/auth/setup", json={
            "username": "second.owner",
            "display_name": "Second Owner",
            "password": "another-long-password",
        })
        self.assertEqual(response.status_code, 409)

        self.client.post("/api/auth/logout")
        response = self.client.post("/api/auth/login", json={
            "username": "viewer.test",
            "password": "another-long-password",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.post("/api/departments", json={"name": "Blocked"}).status_code, 403)
        self.assertEqual(self.client.get("/api/auth/users").status_code, 403)


if __name__ == "__main__":
    unittest.main()