import unittest
import requests

# 定义全局变量
GLOBAL_ACCESS_TOKEN = None
GLOBAL_REFRESH_TOKEN = None
GLOBAL_IMAGE_ID1 = None
GLOBAL_IMAGE_ID2 = None
GLOBAL_ALBUM_LOCATION = None

class TestAlbumAPI(unittest.TestCase):
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

    def test_02_create_image1(self):
        global GLOBAL_IMAGE_ID1
        response = requests.post(
            f"{self.BASE_URL}/images",
            headers={"Authorization": f"Bearer {GLOBAL_ACCESS_TOKEN}"},
            json={"description": "test", "visibility": 0},
        )
        self.assertEqual(response.status_code, 201)
        GLOBAL_IMAGE_ID1 = response.headers["Location"].split("/")[-1]

    def test_03_create_image2(self):
        global GLOBAL_IMAGE_ID2
        response = requests.post(
            f"{self.BASE_URL}/images",
            headers={"Authorization": f"Bearer {GLOBAL_ACCESS_TOKEN}"},
            json={"description": "test", "visibility": 0},
        )
        self.assertEqual(response.status_code, 201)
        GLOBAL_IMAGE_ID2 = response.headers["Location"].split("/")[-1]

    def test_04_create_album(self):
        global GLOBAL_ALBUM_LOCATION
        response = requests.post(
            f"{self.BASE_URL}/albums",
            headers={"Authorization": f"Bearer {GLOBAL_ACCESS_TOKEN}"},
            json={"album_name": "test", "description": "test", "visibility": 0, "images": [GLOBAL_IMAGE_ID1, GLOBAL_IMAGE_ID2]},
        )
        self.assertEqual(response.status_code, 201)
        GLOBAL_ALBUM_LOCATION = response.headers["Location"]

    def test_05_get_album(self):
        response = requests.get(
            f"{self.BASE_URL}{GLOBAL_ALBUM_LOCATION}",
            headers={"Authorization": f"Bearer {GLOBAL_ACCESS_TOKEN}"},
        )
        self.assertEqual(response.status_code, 200)

    def test_06_update_album(self):
        response = requests.put(
            f"{self.BASE_URL}{GLOBAL_ALBUM_LOCATION}",
            headers={"Authorization": f"Bearer {GLOBAL_ACCESS_TOKEN}"},
            json={"album_name": "test", "description": "test2", "visibility": 1, "images": [GLOBAL_IMAGE_ID1]},
        )
        self.assertEqual(response.status_code, 200)

    def test_07_get_album_again(self):
        response = requests.get(
            f"{self.BASE_URL}{GLOBAL_ALBUM_LOCATION}",
            headers={"Authorization": f"Bearer {GLOBAL_ACCESS_TOKEN}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["description"], "test2")

    def test_08_delete_album(self):
        response = requests.delete(
            f"{self.BASE_URL}{GLOBAL_ALBUM_LOCATION}",
            headers={"Authorization": f"Bearer {GLOBAL_ACCESS_TOKEN}"},
        )
        self.assertEqual(response.status_code, 200)

    def test_09_get_album_again(self):
        response = requests.get(
            f"{self.BASE_URL}{GLOBAL_ALBUM_LOCATION}",
            headers={"Authorization": f"Bearer {GLOBAL_ACCESS_TOKEN}"},
        )
        self.assertEqual(response.status_code, 404)

    def test_10_logout(self):
        response = requests.delete(
            f"{self.BASE_URL}/session",
            headers={"Authorization": f"Bearer {GLOBAL_REFRESH_TOKEN}"},
        )
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()