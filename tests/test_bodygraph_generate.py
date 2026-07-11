import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Add workspace paths to sys.path
WORKSPACE_PATH = "/home/ubuntu/work/hd-platform"
BODYGRAPH_PATH = "/home/ubuntu/work/hd-bodygraph"

if WORKSPACE_PATH not in sys.path:
    sys.path.insert(0, WORKSPACE_PATH)
if BODYGRAPH_PATH not in sys.path:
    sys.path.insert(0, BODYGRAPH_PATH)

from api.main import app
from api.routes.bodygraph import BodygraphGenerateRequest
import bridge


class TestBodygraphGenerateUnit(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    # Unit Test 1: Request Validation
    def test_request_validation_coords(self):
        """Test that lat and lon must both be provided or both omitted."""
        # 1. Both provided -> OK
        req = BodygraphGenerateRequest(
            name="Test", year=1990, month=1, day=1, hour=12, lat=40.71, lon=-74.0
        )
        self.assertEqual(req.lat, 40.71)
        self.assertEqual(req.lon, -74.0)

        # 2. Both omitted -> OK
        req2 = BodygraphGenerateRequest(
            name="Test", year=1990, month=1, day=1, hour=12
        )
        self.assertIsNone(req2.lat)
        self.assertIsNone(req2.lon)

        # 3. Only lat provided -> ValidationError
        with self.assertRaises(ValueError):
            BodygraphGenerateRequest(
                name="Test", year=1990, month=1, day=1, hour=12, lat=40.71
            )

        # 4. Only lon provided -> ValidationError
        with self.assertRaises(ValueError):
            BodygraphGenerateRequest(
                name="Test", year=1990, month=1, day=1, hour=12, lon=-74.0
            )

    # Unit Test 2: Center and Gate Mapping in bridge
    def test_bridge_chart_to_gonzih_mapping(self):
        """Test that bridge.chart_to_gonzih maps defined center names and gates correctly."""
        mock_chart = {
            "name": "Mock",
            "defined_centers": ["Head", "Heart", "Solar Plexus"],
            "personality_planets": {
                "Sun": {"gate": 1, "line": 2, "color": 1, "tone": 1, "base": 1}
            },
            "design_planets": {
                "Sun": {"gate": 1, "line": 5, "color": 2, "tone": 2, "base": 2},
                "Earth": {"gate": 2, "line": 1}
            },
            "defined_channels": [
                {"gates": (1, 8), "name": "Inspiration"}
            ],
            "hd_type": "Generator",
            "profile": "2/4",
            "definition": "Single",
            "authority": "Emotional",
            "strategy": "To Respond"
        }
        
        gonzih = bridge.chart_to_gonzih(mock_chart)
        
        # Check center mapping (Heart -> Ego, Solar Plexus -> SolarPlexus)
        self.assertIn("Head", gonzih["definedCenters"])
        self.assertIn("Ego", gonzih["definedCenters"])
        self.assertIn("SolarPlexus", gonzih["definedCenters"])
        
        # Check gates mapping
        self.assertEqual(gonzih["bothGates"], [1])
        self.assertEqual(gonzih["designGates"], [2])
        self.assertEqual(gonzih["personalityGates"], [])
        
        # Check channels
        self.assertEqual(gonzih["channels"], [[1, 8]])

    # Unit Test 3: API Engine Error Handling (mocked)
    @patch("api.routes.bodygraph.compute_natal_chart")
    def test_endpoint_engine_error(self, mock_compute):
        """Test that the route returns error response when engine fails or returns error."""
        # 1. Engine returns error dict
        mock_compute.return_value = {"error": True, "detail": "Mock Ephemeris Error"}
        
        payload = {
            "name": "Test",
            "year": 1990,
            "month": 1,
            "day": 1,
            "hour": 12
        }
        response = self.client.post("/v1/bodygraph/generate/noauth", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], "Mock Ephemeris Error")

        # 2. Engine raises exception
        mock_compute.side_effect = Exception("Fatal Calculation Crash")
        response = self.client.post("/v1/bodygraph/generate/noauth", json=payload)
        self.assertEqual(response.status_code, 502)
        self.assertIn("Engine unavailable", response.json()["detail"])

    # Unit Test 4: Route Handling of Rendering Failures
    @patch("api.routes.bodygraph.compute_natal_chart")
    @patch("bridge.render_svg")
    def test_endpoint_rendering_failure(self, mock_render_svg, mock_compute):
        """Test API behavior when the renderer returns empty SVG."""
        mock_compute.return_value = {
            "defined_centers": [],
            "personality_planets": {},
            "design_planets": {},
        }
        mock_render_svg.return_value = ""  # Failure to render
        
        payload = {
            "name": "Test",
            "year": 1990,
            "month": 1,
            "day": 1,
            "hour": 12
        }
        response = self.client.post("/v1/bodygraph/generate/noauth", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], "Failed to render SVG bodygraph")

    # Unit Test 5: Theme Option Propagation
    @patch("api.routes.bodygraph.compute_natal_chart")
    @patch("bridge.render_svg")
    def test_endpoint_theme_propagation(self, mock_render_svg, mock_compute):
        """Test that the requested theme option is passed through to the renderer."""
        mock_compute.return_value = {
            "defined_centers": [],
            "personality_planets": {},
            "design_planets": {},
        }
        mock_render_svg.return_value = "<svg></svg>"
        
        payload = {
            "name": "Test",
            "year": 1990,
            "month": 1,
            "day": 1,
            "hour": 12,
            "theme": "dark"
        }
        response = self.client.post("/v1/bodygraph/generate/noauth", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        
        # Verify that mock_render_svg was called with theme="dark"
        mock_render_svg.assert_called_with(unittest.mock.ANY, theme="dark")


class TestBodygraphGenerateIntegration(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    # Integration Test 1: Complete End-To-End Calculation and Rendering
    def test_integration_full_bodygraph_generate(self):
        """E2E integration test: computes, maps, renders, and returns full SVG + metadata."""
        payload = {
            "name": "Jane E2E",
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
        response = self.client.post("/v1/bodygraph/generate/noauth", json=payload)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["endpoint"], "/v1/bodygraph/generate")
        
        # Check SVG presence and structure
        svg = data["svg"]
        self.assertIsNotNone(svg)
        self.assertTrue(svg.strip().startswith("<svg"))
        self.assertTrue(svg.strip().endswith("</svg>"))
        
        # Check metadata values computed via hd-bodygraph mapping logic
        meta = data["metadata"]
        self.assertIsNotNone(meta)
        self.assertEqual(meta["type"], "Projector")
        self.assertEqual(meta["profile"], "6/2")
        self.assertEqual(meta["authority"], "Self-Projected")
        self.assertEqual(meta["strategy"], "To Wait for Invitation")
        
        # Check defined Centers structure
        self.assertIn("definedCenters", meta)
        self.assertEqual(sorted(meta["definedCenters"]), sorted(["G", "Throat"]))
        
        # Check gates structure
        self.assertIn("gates", meta)
        self.assertEqual(len(meta["gates"]), 64)
