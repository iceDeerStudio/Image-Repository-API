import unittest
import requests

# 定义全局变量
GLOBAL_ACCESS_TOKEN = None
GLOBAL_REFRESH_TOKEN = None
GLOBAL_IMAGE_ID = None

class TestImageAPI(unittest.TestCase):
    BASE_URL = "http://127.0.0.1:5000"

    @classmethod
    def setUpClass(cls):
        # 在测试开始前重置数据库
        requests.get(f"{cls.BASE_URL}/util/drop")
        requests.get(f"{cls.BASE_URL}/util/init")

    def test_01_login(self):
        global GLOBAL_ACCESS_TOKEN, GLOBAL_REFRESH_TOKEN
        response = requests.post(
            f"{self.BASE_URL}/session",
            json={"username": "admin", "password": "admin"},
        )
        self.assertEqual(response.status_code, 200)
        GLOBAL_ACCESS_TOKEN = response.json()["access_token"]
        GLOBAL_REFRESH_TOKEN = response.json()["refresh_token"]

    def test_02_create_image(self):
        global GLOBAL_IMAGE_ID
        response = requests.post(
            f"{self.BASE_URL}/images",
            headers={"Authorization": f"Bearer {GLOBAL_ACCESS_TOKEN}"},
            json={"description": "test", "visibility": 0},
        )
        self.assertEqual(response.status_code, 201)
        GLOBAL_IMAGE_ID = response.headers["Location"].split("/")[-1]

    def test_03_get_image(self):
        response = requests.get(
            f"{self.BASE_URL}/images/{GLOBAL_IMAGE_ID}",
            headers={"Authorization": f"Bearer {GLOBAL_ACCESS_TOKEN}"},
        )
        self.assertEqual(response.status_code, 200)

    def test_04_upload_image(self):
        with open("tests/test.png", "rb") as file:
            response = requests.post(
                f"{self.BASE_URL}/images/{GLOBAL_IMAGE_ID}/file",
                headers={"Authorization": f"Bearer {GLOBAL_ACCESS_TOKEN}"},
                files={"file": file},
            )
        self.assertEqual(response.status_code, 200)

    def test_05_update_image(self):
        response = requests.put(
            f"{self.BASE_URL}/images/{GLOBAL_IMAGE_ID}",
            headers={"Authorization": f"Bearer {GLOBAL_ACCESS_TOKEN}"},
            json={"description": "test2", "visibility": 1},
        )
        self.assertEqual(response.status_code, 200)

    def test_06_get_image_file(self):
        response = requests.get(
            f"{self.BASE_URL}/images/{GLOBAL_IMAGE_ID}/file",
            headers={"Authorization": f"Bearer {GLOBAL_ACCESS_TOKEN}"},
        )
        self.assertEqual(response.status_code, 200)

    def test_07_get_images(self):
        response = requests.get(
            f"{self.BASE_URL}/images",
            headers={"Authorization": f"Bearer {GLOBAL_ACCESS_TOKEN}"},
        )
        self.assertEqual(response.status_code, 200)

    def test_08_delete_image(self):
        response = requests.delete(
            f"{self.BASE_URL}/images/{GLOBAL_IMAGE_ID}",
            headers={"Authorization": f"Bearer {GLOBAL_ACCESS_TOKEN}"},
        )
        self.assertEqual(response.status_code, 200)

    def test_09_logout(self):
        response = requests.delete(
            f"{self.BASE_URL}/session",
            headers={"Authorization": f"Bearer {GLOBAL_REFRESH_TOKEN}"},
        )
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()