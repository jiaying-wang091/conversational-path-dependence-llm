from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from path_dependence.provider import OpenAIResponsesProvider


class ProviderPayloadTests(unittest.TestCase):
    def test_approved_payload(self) -> None:
        with patch.dict(os.environ, {"OPENAI_API_KEY": "offline-test-key"}):
            provider = OpenAIResponsesProvider(
                model="gpt-5.6-sol",
                reasoning_effort="none",
                temperature=0,
                top_p=1,
                max_output_tokens=1500,
                seed=None,
                base_url="https://api.openai.com/v1",
            )
        payload = provider.request_payload(
            [{"role": "user", "content": "offline validation"}]
        )
        self.assertEqual(payload["model"], "gpt-5.6-sol")
        self.assertEqual(payload["reasoning"], {"effort": "none"})
        self.assertEqual(payload["temperature"], 0)
        self.assertEqual(payload["top_p"], 1)
        self.assertEqual(payload["max_output_tokens"], 1500)
        self.assertFalse(payload["store"])
        self.assertNotIn("seed", payload)


if __name__ == "__main__":
    unittest.main()
