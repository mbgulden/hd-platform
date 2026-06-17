import sys
import os
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient

# Add workspace paths to sys.path
WORKSPACE_PATH = "/home/ubuntu/work/hd-platform"
if WORKSPACE_PATH not in sys.path:
    sys.path.insert(0, WORKSPACE_PATH)

from api.main import app
from shared.llm_interpreter import (
    compute_birth_data_hash,
    generate_interpretation,
    _generate_template_fallback
)


class TestLLMInterpretationUnit(unittest.IsolatedAsyncioTestCase):
    
    def test_compute_birth_data_hash_stability(self):
        """Test that hashing is stable and normalizes coordinates/timezone."""
        birth1 = {
            "year": 1990, "month": 6, "day": 1, "hour": 8, "minute": 0,
            "lat": 40.7128, "lon": -74.0060, "timezone": "America/New_York "
        }
        birth2 = {
            "year": 1990, "month": 6, "day": 1, "hour": 8, "minute": 0,
            "lat": 40.71284, "lon": -74.00601, "timezone": "America/New_York"
        }
        
        # Rounding to 4 decimals: 40.7128 and -74.0060 for both
        hash1 = compute_birth_data_hash(birth1)
        hash2 = compute_birth_data_hash(birth2)
        self.assertEqual(hash1, hash2)

    def test_template_fallback_structure(self):
        """Test that fallback template generates correct Markdown headers and keywords."""
        mock_chart = {
            "name": "Jane Test",
            "hd_type": "Manifesting Generator",
            "profile": "3/5",
            "authority": "Sacral",
            "strategy": "To Respond",
            "signature": "Satisfaction",
            "not_self_theme": "Frustration",
            "incarnation_cross": {"name": "Left Angle Cross of Alignment"},
            "defined_centers": ["Sacral", "Throat", "G"],
            "undefined_centers": ["Head", "Ajna", "Heart"],
            "defined_channels": [{"gates": (34, 20), "name": "Charisma"}]
        }
        
        fallback_text = _generate_template_fallback(mock_chart)
        
        # Verify required headers
        self.assertIn("## Core Alignment (Type, Authority & Strategy)", fallback_text)
        self.assertIn("## Key Energy Patterns & Gifts (Channels & Centers)", fallback_text)
        self.assertIn("## Life Theme & Purpose (Incarnation Cross)", fallback_text)
        
        # Verify placeholder variables
        self.assertIn("Manifesting Generator", fallback_text)
        self.assertIn("Sacral", fallback_text)
        self.assertIn("To Respond", fallback_text)
        self.assertIn("Charisma", fallback_text)
        self.assertIn("Left Angle Cross of Alignment", fallback_text)

    @patch("shared.llm_interpreter.call_anthropic_api", new_callable=AsyncMock)
    @patch("shared.llm_interpreter.get_cached_interpretation", new_callable=AsyncMock)
    @patch("shared.llm_interpreter.save_cached_interpretation", new_callable=AsyncMock)
    async def test_generate_interpretation_calls_api_on_cache_miss(
        self, mock_save, mock_get_cache, mock_call_api
    ):
        """Test that API is called when cache misses and results are saved."""
        mock_get_cache.return_value = None
        mock_call_api.return_value = "Mock Claude Response Output"
        
        mock_chart = {"name": "Test User"}
        birth_data = {"year": 1990}
        
        interp, provider = await generate_interpretation(mock_chart, birth_data)
        
        self.assertEqual(interp, "Mock Claude Response Output")
        self.assertEqual(provider, "anthropic-claude")
        
        # Verify it saved to cache
        mock_save.assert_called_once()
        mock_call_api.assert_called_once()

    @patch("shared.llm_interpreter.get_cached_interpretation", new_callable=AsyncMock)
    @patch("shared.llm_interpreter.call_anthropic_api", new_callable=AsyncMock)
    async def test_generate_interpretation_uses_cache_on_hit(
        self, mock_call_api, mock_get_cache
    ):
        """Test that API call is skipped if cache hit occurs."""
        mock_get_cache.return_value = {
            "interpretation": "Cached Interpretation Content",
            "provider": "anthropic-claude"
        }
        
        mock_chart = {"name": "Test User"}
        birth_data = {"year": 1990}
        
        interp, provider = await generate_interpretation(mock_chart, birth_data)
        
        self.assertEqual(interp, "Cached Interpretation Content")
        self.assertEqual(provider, "anthropic-claude")
        
        # Verify API was NOT called
        mock_call_api.assert_not_called()


class TestLLMInterpretationIntegration(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_endpoint_returns_interpretation(self):
        """E2E test: verifies that endpoints return interpretation field."""
        payload = {
            "name": "Jane Doe",
            "year": 1990,
            "month": 6,
            "day": 1,
            "hour": 8,
            "minute": 0,
            "lat": 40.71,
            "lon": -74.0,
            "timezone": "America/New_York",
            "theme": "canonical"
        }
        
        # 1. Test generate/noauth
        response = self.client.post("/v1/bodygraph/generate/noauth", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("interpretation", data)
        self.assertIsNotNone(data["interpretation"])
        self.assertTrue(data["interpretation"].startswith("## Core Alignment"))

        # 2. Test bodygraph/noauth
        response = self.client.post("/v1/bodygraph/noauth", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("interpretation", data["data"])
        self.assertIsNotNone(data["data"]["interpretation"])
        self.assertTrue(data["data"]["interpretation"].startswith("## Core Alignment"))
