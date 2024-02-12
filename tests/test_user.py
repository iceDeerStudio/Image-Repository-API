import unittest
import requests

# 定义全局变量
GLOBAL_ACCESS_TOKEN = None
GLOBAL_REFRESH_TOKEN = None
GLOBAL_USER_LOCATION = None


class TestUserAPI(unittest.TestCase):
    BASE_URL = "http://127.0.0.1:5000"

    @classmethod
    def setUpClass(cls):
        # 在测试开始前重置数据库
        requests.get(f"{cls.BASE_URL}/utils/drop")
        requests.get(f"{cls.BASE_URL}/utils/init")

    def test_01_register(self):
        global GLOBAL_USER_LOCATION
        response = requests.post(
            f"{self.BASE_URL}/user",
            json={
                "username": "test",
                "nickname": "test",
                "password": "test",
                "permission_level": 1,
            },
        )
        self.assertEqual(response.status_code, 201)
        GLOBAL_USER_LOCATION = response.headers["Location"]

    def test_02_login(self):
        global GLOBAL_ACCESS_TOKEN, GLOBAL_REFRESH_TOKEN
        response = requests.post(
            f"{self.BASE_URL}/user/login",
            json={"username": "test", "password": "test"},
        )
        self.assertEqual(response.status_code, 200)
        GLOBAL_ACCESS_TOKEN = response.json()["access_token"]
        GLOBAL_REFRESH_TOKEN = response.json()["refresh_token"]

    def test_03_get_user(self):
        response = requests.get(
            f"{self.BASE_URL}{GLOBAL_USER_LOCATION}",
            headers={"Authorization": f"Bearer {GLOBAL_ACCESS_TOKEN}"},
        )
        self.assertEqual(response.status_code, 200)

    def test_04_update_user(self):
        response = requests.put(
            f"{self.BASE_URL}{GLOBAL_USER_LOCATION}",
            headers={"Authorization": f"Bearer {GLOBAL_ACCESS_TOKEN}"},
            json={"username": "test", "nickname": "test2", "password": "test2", "permission_level": 1},
        )
        self.assertEqual(response.status_code, 200)

    def test_05_refresh_token(self):
        global GLOBAL_ACCESS_TOKEN, GLOBAL_REFRESH_TOKEN
        response = requests.post(
            f"{self.BASE_URL}/user/refresh",
            headers={"Authorization": f"Bearer {GLOBAL_REFRESH_TOKEN}"},
        )
        self.assertEqual(response.status_code, 200)
        GLOBAL_ACCESS_TOKEN = response.json()["access_token"]

    def test_06_get_user_again(self):
        response = requests.get(
            f"{self.BASE_URL}{GLOBAL_USER_LOCATION}",
            headers={"Authorization": f"Bearer {GLOBAL_ACCESS_TOKEN}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["nickname"], "test2")

    def test_07_logout(self):
        response = requests.post(
            f"{self.BASE_URL}/user/logout",
            headers={"Authorization": f"Bearer {GLOBAL_REFRESH_TOKEN}"},
        )
        self.assertEqual(response.status_code, 200)

    def test_08_refresh_token_again(self):
        response = requests.post(
            f"{self.BASE_URL}/user/refresh",
            headers={"Authorization": f"Bearer {GLOBAL_REFRESH_TOKEN}"},
        )
        self.assertEqual(response.status_code, 401)

    def test_09_login_as_admin(self):
        global GLOBAL_ACCESS_TOKEN, GLOBAL_REFRESH_TOKEN
        response = requests.post(
            f"{self.BASE_URL}/user/login",
            json={"username": "admin", "password": "admin"},
        )
        self.assertEqual(response.status_code, 200)
        GLOBAL_ACCESS_TOKEN = response.json()["access_token"]
        GLOBAL_REFRESH_TOKEN = response.json()["refresh_token"]

    def test_10_delete_user(self):
        response = requests.delete(
            f"{self.BASE_URL}{GLOBAL_USER_LOCATION}",
            headers={"Authorization": f"Bearer {GLOBAL_ACCESS_TOKEN}"},
        )
        self.assertEqual(response.status_code, 200)

    def test_11_get_user_again(self):
        response = requests.get(
            f"{self.BASE_URL}{GLOBAL_USER_LOCATION}",
            headers={"Authorization": f"Bearer {GLOBAL_ACCESS_TOKEN}"},
        )
        self.assertEqual(response.status_code, 404)

    def test_12_create_admin_user(self):
        response = requests.post(
            f"{self.BASE_URL}/user",
            headers={"Authorization": f"Bearer {GLOBAL_ACCESS_TOKEN}"},
            json={
                "username": "admin1",
                "nickname": "admin1",
                "password": "admin1",
                "permission_level": 2,
            },
        )
        self.assertEqual(response.status_code, 201)

    def test_13_logout_as_admin(self):
        response = requests.post(
            f"{self.BASE_URL}/user/logout",
            headers={"Authorization": f"Bearer {GLOBAL_REFRESH_TOKEN}"},
        )
        self.assertEqual(response.status_code, 200)

    def test_14_create_admin_user_without_permission(self):
        response = requests.post(
            f"{self.BASE_URL}/user",
            json={
                "username": "admin2",
                "nickname": "admin2",
                "password": "admin2",
                "permission_level": 2,
            },
        )
        self.assertEqual(response.status_code, 403)


if __name__ == "__main__":
    unittest.main()
