"""API integration tests — the mobile acceptance scenario over HTTP,
including realtime WebSocket delivery and device registration.
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

_tmp = tempfile.mkdtemp(prefix="silver_api_test_")
os.environ["SILVER_DATA_DIR"] = _tmp

from silver import db  # noqa: E402

db.DATA_DIR = Path(_tmp)
db.MEDIA_DIR = db.DATA_DIR / "media"
db.DB_PATH = db.DATA_DIR / "silver.db"

from fastapi.testclient import TestClient  # noqa: E402

from backend.main import app  # noqa: E402

client = TestClient(app)


def auth(token):
    return {"Authorization": f"Bearer {token}"}


class ApiScenarioTest(unittest.TestCase):
    @staticmethod
    def _register_or_login(username, email, name):
        r = client.post("/auth/register", json={
            "username": username, "email": email,
            "password": "password123", "display_name": name})
        if r.status_code != 200:  # another test module already created this user
            r = client.post("/auth/login", json={
                "identifier": username, "password": "password123"})
        assert r.status_code == 200, r.text
        return r.json()

    @classmethod
    def setUpClass(cls):
        a = cls._register_or_login("api_amal", "api_a@x.com", "أمل")
        cls.ta, cls.uid_a = a["token"], a["user"]["id"]
        b = cls._register_or_login("api_badr", "api_b@x.com", "بدر")
        cls.tb, cls.uid_b = b["token"], b["user"]["id"]

    def test_01_health(self):
        r = client.get("/health")
        self.assertEqual(r.json()["status"], "ok")

    def test_02_interests_profile_follow(self):
        cats = client.get("/categories").json()
        tech = next(c["id"] for c in cats if c["slug"] == "tech")
        self.assertEqual(client.put("/me/interests", json={"category_ids": [tech]},
                                    headers=auth(self.tb)).status_code, 200)
        client.put("/me", json={"city": "Riyadh"}, headers=auth(self.ta))
        client.put("/me", json={"city": "Riyadh"}, headers=auth(self.tb))
        self.assertTrue(client.post(f"/users/{self.uid_a}/follow",
                                    headers=auth(self.tb)).json()["following"])
        self.assertTrue(client.post(f"/users/{self.uid_b}/follow",
                                    headers=auth(self.ta)).json()["following"])

    def test_03_adaptive_post_and_feeds(self):
        cats = client.get("/categories").json()
        tech = next(c["id"] for c in cats if c["slug"] == "tech")
        sug = client.post("/assistant/suggest", json={"text": "منشور عن التقنية والبرمجة"},
                          headers=auth(self.ta)).json()
        self.assertEqual(sug["category"], "tech")
        r = client.post("/posts", json={
            "body": "منشور تقني", "audiences": ["circle", "front", "interests"],
            "category_id": tech}, headers=auth(self.ta))
        self.assertEqual(r.status_code, 200, r.text)
        pid = r.json()["id"]
        for section in ["circle", "front", "interests"]:
            feed = client.get(f"/feed/{section}", headers=auth(self.tb)).json()
            self.assertIn(pid, [p["id"] for p in feed], section)
        self.assertTrue(client.post(f"/posts/{pid}/like",
                                    headers=auth(self.tb)).json()["liked"])
        self.assertEqual(client.post(f"/posts/{pid}/comments", json={"body": "رائع"},
                                     headers=auth(self.tb)).status_code, 200)
        type(self).pid = pid

    def test_04_realtime_message_over_websocket(self):
        with client.websocket_connect(f"/ws?token={self.ta}") as ws:
            r = client.post("/conversations", json={"user_id": self.uid_a},
                            headers=auth(self.tb))
            cid = r.json()["id"]
            client.post(f"/conversations/{cid}/messages", json={"body": "مرحبا"},
                        headers=auth(self.tb))
            event = ws.receive_json()
            self.assertEqual(event["type"], "message")
            self.assertEqual(event["conversation_id"], cid)
        msgs = client.get(f"/conversations/{cid}/messages", headers=auth(self.ta)).json()
        self.assertEqual(msgs[-1]["body"], "مرحبا")

    def test_05_live_with_ws_chat_and_rtc(self):
        r = client.post("/live", json={"title": "بث تقني"}, headers=auth(self.ta))
        sid = r.json()["id"]
        with client.websocket_connect(f"/ws/live/{sid}?token={self.ta}") as ws:
            client.post(f"/live/{sid}/comments", json={"body": "أهلا"},
                        headers=auth(self.tb))
            event = ws.receive_json()
            self.assertEqual(event["type"], "live_comment")
            self.assertEqual(event["body"], "أهلا")
        # rtc token endpoint responds; disabled without LiveKit env config
        rtc = client.get(f"/live/{sid}/rtc-token", headers=auth(self.ta)).json()
        self.assertIn("enabled", rtc)
        self.assertFalse(rtc["enabled"])
        client.post(f"/live/{sid}/guest-request", headers=auth(self.tb))
        client.post(f"/live/{sid}/guest-action",
                    json={"user_id": self.uid_b, "status": "approved"}, headers=auth(self.ta))
        detail = client.get(f"/live/{sid}", headers=auth(self.tb)).json()
        self.assertEqual(detail["guests"][0]["status"], "approved")
        client.post(f"/live/{sid}/end?keep_recording=true", headers=auth(self.ta))

    def test_06_devices_and_admin(self):
        r = client.post("/devices", json={"push_token": "ExponentPushToken[test]",
                                          "platform": "android"}, headers=auth(self.ta))
        self.assertEqual(r.status_code, 200)
        rep = client.post("/reports", json={
            "target_kind": "post", "target_id": type(self).pid,
            "reason": "reason_spam"}, headers=auth(self.tb)).json()
        adm = client.post("/auth/login", json={
            "identifier": os.environ.get("SILVER_ADMIN_USERNAME", "admin"),
            "password": os.environ.get("SILVER_ADMIN_PASSWORD", "ChangeMe_123")}).json()
        tadm = adm["token"]
        reports = client.get("/admin/reports", headers=auth(tadm)).json()
        self.assertIn(rep["id"], [x["id"] for x in reports])
        client.post(f"/admin/reports/{rep['id']}/resolve", json={"action": "hide_post"},
                    headers=auth(tadm))
        feed = client.get("/feed/front", headers=auth(self.tb)).json()
        self.assertNotIn(type(self).pid, [p["id"] for p in feed])
        # role separation
        self.assertEqual(client.get("/admin/stats", headers=auth(self.tb)).status_code, 403)
        self.assertEqual(client.get("/me", headers=auth("xx.yy")).status_code, 401)

    def test_07_websocket_rejects_bad_token(self):
        from starlette.websockets import WebSocketDisconnect
        with self.assertRaises(WebSocketDisconnect):
            with client.websocket_connect("/ws?token=bad.token") as ws:
                ws.receive_text()


if __name__ == "__main__":
    unittest.main(verbosity=2)
