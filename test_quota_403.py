import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))
import sufy_image2 as sf


class Quota403Tests(unittest.TestCase):
    def test_quota_403_is_reported_as_quota(self):
        payload = (
            '{"error":{"message":"token quota is not enough, token remain quota: 积分1.542240, '
            'need quota: 积分3.000024","type":"new_api_error","code":"pre_consume_token_quota_failed"}}'
        )
        body = payload.encode("utf-8")
        client = sf.SfImage2Client(api_key="secret-key")
        error = client._http_error(403, body)
        self.assertIn("token quota is not enough", str(error))
        self.assertNotIn("authentication failed", str(error))

    def test_plain_403_stays_an_auth_error(self):
        client = sf.SfImage2Client(api_key="secret-key")
        error = client._http_error(403, b"")
        self.assertEqual(str(error), "LTS4AI authentication failed (HTTP 403).")

    def test_401_never_leaks_quota_wording(self):
        client = sf.SfImage2Client(api_key="secret-key")
        error = client._http_error(401, b'{"error":{"message":"quota"}}')
        self.assertEqual(str(error), "LTS4AI authentication failed (HTTP 401).")


if __name__ == "__main__":
    unittest.main()
