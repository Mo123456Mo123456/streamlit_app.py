"""Acceptance test for Silver — mirrors section 27 of the product spec:
register → interests → profile → follow → adaptive post → feeds → DM →
story reply → community → community post → live stream → discover →
guest request → end stream → report → block → admin sees report.
"""
import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Point the data dir at a temp location before importing the package.
_tmp = tempfile.mkdtemp(prefix="silver_test_")
os.environ["SILVER_DATA_DIR"] = _tmp

from silver import db, auth, services, ai  # noqa: E402

db.DATA_DIR = Path(_tmp)
db.MEDIA_DIR = db.DATA_DIR / "media"
db.DB_PATH = db.DATA_DIR / "silver.db"


class SilverAcceptanceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conn = db.get_conn()
        db.init_db(cls.conn)
        auth.ensure_admin(cls.conn)

    def test_full_scenario(self):
        conn = self.conn

        # 1-2. Register two users and pick interests.
        uid_a, err = auth.register(conn, "amal", "amal@example.com", "password123", "أمل")
        self.assertEqual(err, "")
        uid_b, err = auth.register(conn, "badr", "badr@example.com", "password123", "بدر")
        self.assertEqual(err, "")
        tech = conn.execute("SELECT id FROM categories WHERE slug='tech'").fetchone()["id"]
        conn.execute("INSERT INTO user_interests (user_id, category_id) VALUES (?,?)", (uid_b, tech))

        # 3. Profile data.
        conn.execute("UPDATE profiles SET city='Riyadh', bio='hello' WHERE user_id=?", (uid_a,))
        conn.execute("UPDATE profiles SET city='Riyadh' WHERE user_id=?", (uid_b,))
        conn.commit()

        # 4. Follow (mutual → friends).
        services.follow(conn, uid_b, uid_a)
        services.follow(conn, uid_a, uid_b)
        self.assertTrue(services.are_friends(conn, uid_a, uid_b))

        # 5-7. Adaptive post targeted at multiple sections appears in right feeds.
        pid = services.create_post(
            conn, uid_a, "منشور عن التقنية والبرمجة", "text",
            ["circle", "front", "interests", "nearby"], category_id=tech, city="Riyadh",
        )
        self.assertIn(pid, [p["id"] for p in services.feed_circle(conn, uid_b)])
        self.assertIn(pid, [p["id"] for p in services.feed_front(conn, uid_b)])
        self.assertIn(pid, [p["id"] for p in services.feed_interests(conn, uid_b)])
        self.assertIn(pid, [p["id"] for p in services.feed_nearby(conn, uid_b, "Riyadh")])

        # Assistant suggestions are advisory only.
        self.assertEqual(ai.suggest_category("منشور عن التقنية والبرمجة"), "tech")
        self.assertTrue(ai.sensitive_warnings("password: hunter2"))

        # Likes / comments / saves.
        self.assertTrue(services.toggle_like(conn, uid_b, pid))
        services.add_comment(conn, pid, uid_b, "رائع!")
        self.assertTrue(services.toggle_save(conn, uid_b, pid))
        post = services.get_post(conn, pid)
        self.assertEqual(post["likes"], 1)
        self.assertEqual(post["comment_count"], 1)

        # 8. Direct message.
        self.assertTrue(services.can_message(conn, uid_b, uid_a))
        cid = services.get_or_create_direct(conn, uid_b, uid_a)
        services.send_message(conn, cid, uid_b, "مرحبا")
        msgs = services.conversation_messages(conn, cid)
        self.assertEqual(msgs[-1]["body"], "مرحبا")

        # 9. Story + reply to story lands in the same DM thread.
        sid = services.create_story(conn, uid_a, "قصتي اليوم", "circle")
        visible = [s["id"] for s in services.visible_stories(conn, uid_b)]
        self.assertIn(sid, visible)
        services.mark_story_viewed(conn, sid, uid_b)
        self.assertEqual(services.story_view_count(conn, sid), 1)
        services.send_message(conn, cid, uid_b, "رد على القصة", story_id=sid)
        self.assertEqual(services.conversation_messages(conn, cid)[-1]["story_id"], sid)

        # 10-11. Community: join + post inside it.
        comm = services.create_community(conn, uid_a, "مجتمع التقنية", "نقاش تقني", "public", tech)
        self.assertEqual(services.join_community(conn, comm, uid_b), "active")
        cpid = services.create_post(conn, uid_b, "منشور داخل المجتمع", "text",
                                    ["communities"], community_id=comm)
        self.assertIn(cpid, [p["id"] for p in services.community_posts(conn, comm)])
        self.assertIn(cpid, [p["id"] for p in services.feed_communities(conn, uid_a)])

        # 12-17. Public live stream: discover, viewer, guest request, approve, end+save.
        stream = services.start_stream(conn, uid_a, "بث تقني", "حوار مباشر", tech)
        self.assertIn(stream, [s["id"] for s in services.live_streams_now(conn)])
        services.join_stream(conn, stream, uid_b)
        services.live_comment(conn, stream, uid_b, "أهلا بالجميع")
        self.assertEqual(services.get_stream(conn, stream)["viewer_count"], 1)
        services.request_guest(conn, stream, uid_b)
        services.set_guest_status(conn, stream, uid_b, "approved")
        guests = services.stream_guests(conn, stream, "approved")
        self.assertEqual(guests[0]["user_id"], uid_b)
        services.end_stream(conn, stream, keep_recording=True)
        self.assertIn(stream, [s["id"] for s in services.saved_streams(conn, uid_a)])

        # 18-19. Report + block; report shows up for admin and is actionable.
        rid = services.create_report(conn, uid_b, "post", pid, "reason_spam", "تجربة")
        self.assertIn(rid, [r["id"] for r in services.open_reports(conn)])
        admin = conn.execute("SELECT id FROM users WHERE role='admin'").fetchone()["id"]
        services.resolve_report(conn, rid, admin, "hide_post")
        self.assertEqual(conn.execute("SELECT hidden FROM posts WHERE id=?", (pid,)).fetchone()[0], 1)
        self.assertNotIn(pid, [p["id"] for p in services.feed_front(conn, uid_b)])

        services.block(conn, uid_b, uid_a)
        self.assertTrue(services.is_blocked_between(conn, uid_a, uid_b))
        self.assertFalse(services.can_message(conn, uid_a, uid_b))
        services.unblock(conn, uid_b, uid_a)

        # Notifications were produced along the way.
        self.assertGreater(len(services.user_notifications(conn, uid_a)), 0)

        # Admin stats reflect the activity.
        stats = services.admin_stats(conn)
        self.assertGreaterEqual(stats["users"], 3)
        self.assertGreaterEqual(stats["posts"], 2)
        self.assertGreaterEqual(stats["streams"], 1)

    def test_message_privacy_settings(self):
        conn = self.conn
        uid_c, _ = auth.register(conn, "carla", "carla@example.com", "password123", "كارلا")
        uid_d, _ = auth.register(conn, "dawod", "dawod@example.com", "password123", "داود")
        conn.execute("UPDATE user_settings SET who_can_message='nobody' WHERE user_id=?", (uid_d,))
        conn.commit()
        self.assertFalse(services.can_message(conn, uid_c, uid_d))
        conn.execute("UPDATE user_settings SET who_can_message='friends' WHERE user_id=?", (uid_d,))
        conn.commit()
        self.assertFalse(services.can_message(conn, uid_c, uid_d))
        services.follow(conn, uid_c, uid_d)
        services.follow(conn, uid_d, uid_c)
        self.assertTrue(services.can_message(conn, uid_c, uid_d))

    def test_auth_validation(self):
        conn = self.conn
        self.assertEqual(auth.register(conn, "x", "e@e.com", "password123", "n")[1], "err_username")
        self.assertEqual(auth.register(conn, "gooduser", "bad", "password123", "n")[1], "err_email")
        self.assertEqual(auth.register(conn, "gooduser", "g@g.com", "short", "n")[1], "err_password_short")
        uid, _ = auth.register(conn, "gooduser", "g@g.com", "password123", "Good")
        self.assertIsNotNone(uid)
        row, err = auth.login(conn, "gooduser", "wrongpass")
        self.assertEqual(err, "err_login")
        row, err = auth.login(conn, "gooduser", "password123")
        self.assertEqual(row["id"], uid)


if __name__ == "__main__":
    unittest.main(verbosity=2)
