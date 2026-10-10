import os
import tempfile
import unittest

from app import create_app


class TaskApiTests(unittest.TestCase):
    def setUp(self):
        fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        self.client = create_app(self.db_path).test_client()

    def tearDown(self):
        os.remove(self.db_path)

    def create(self, **fields):
        body = {"title": "Write report", **fields}
        return self.client.post("/api/tasks", json=body)

    def test_health(self):
        self.assertEqual(self.client.get("/api/health").get_json(), {"status": "ok"})

    def test_create_and_get(self):
        res = self.create(priority="high", due_date="2026-12-01")
        self.assertEqual(res.status_code, 201)
        task = res.get_json()
        self.assertEqual(task["title"], "Write report")
        self.assertEqual(task["priority"], "high")
        self.assertFalse(task["completed"])
        got = self.client.get(f"/api/tasks/{task['id']}").get_json()
        self.assertEqual(got, task)

    def test_validation(self):
        self.assertEqual(self.client.post("/api/tasks", json={"title": "  "}).status_code, 400)
        self.assertEqual(self.create(priority="urgent").status_code, 400)
        self.assertEqual(self.create(due_date="12/01/2026").status_code, 400)

    def test_update_and_filter(self):
        a = self.create(title="A").get_json()
        self.create(title="B")
        res = self.client.patch(f"/api/tasks/{a['id']}", json={"completed": True})
        self.assertTrue(res.get_json()["completed"])
        active = self.client.get("/api/tasks?status=active").get_json()
        done = self.client.get("/api/tasks?status=completed").get_json()
        self.assertEqual([t["title"] for t in active], ["B"])
        self.assertEqual([t["title"] for t in done], ["A"])

    def test_search(self):
        self.create(title="Buy milk")
        self.create(title="Call mom", description="about the trip")
        titles = [t["title"] for t in self.client.get("/api/tasks?q=trip").get_json()]
        self.assertEqual(titles, ["Call mom"])

    def test_sort_by_priority(self):
        self.create(title="low", priority="low")
        self.create(title="high", priority="high")
        titles = [t["title"] for t in self.client.get("/api/tasks").get_json()]
        self.assertEqual(titles, ["high", "low"])

    def test_delete_and_stats(self):
        a = self.create().get_json()
        b = self.create().get_json()
        self.client.patch(f"/api/tasks/{b['id']}", json={"completed": True})
        self.assertEqual(
            self.client.get("/api/stats").get_json(), {"total": 2, "completed": 1, "active": 1}
        )
        self.assertEqual(self.client.delete(f"/api/tasks/{a['id']}").status_code, 204)
        self.assertEqual(self.client.delete(f"/api/tasks/{a['id']}").status_code, 404)
        self.assertEqual(self.client.delete("/api/tasks/completed").get_json(), {"deleted": 1})
        self.assertEqual(self.client.get("/api/stats").get_json()["total"], 0)

    def test_missing_task(self):
        self.assertEqual(self.client.get("/api/tasks/999").status_code, 404)
        self.assertEqual(self.client.patch("/api/tasks/999", json={}).status_code, 404)


if __name__ == "__main__":
    unittest.main()
