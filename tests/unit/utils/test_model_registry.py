# tests/test_model_registry.py
import pytest
from unittest.mock import patch, MagicMock
from app.utils.model_registry import get_model_by_name


class TestModelRegistry:
    def test_get_model_by_name_success(self):
        """Test successful model retrieval by name."""
        with patch("app.utils.model_registry.models") as mock_models:
            # Setup mock
            mock_models.__all__ = ["User", "Post"]
            mock_models.User = MagicMock()

            # Call function
            model_class = get_model_by_name("User")

            # Assert result is correct
            assert model_class == mock_models.User

    def test_get_model_by_name_not_found(self):
        """Test ValueError raised when model not found."""
        with patch("app.utils.model_registry.models") as mock_models:
            # Setup mock
            mock_models.__all__ = ["User", "Post"]
            mock_models.User = MagicMock()

            # Test exception is raised for unknown model
            with pytest.raises(ValueError) as excinfo:
                get_model_by_name("Unknown")

            assert "Unknown model: Unknown" in str(excinfo.value)

    def test_get_model_by_name_logs_error(self):
        """Test error is logged when model not found."""
        with patch("app.utils.model_registry.models") as mock_models, patch("app.utils.model_registry.current_app") as mock_app:
            # Setup mocks
            mock_models.__all__ = ["User"]
            mock_logger = MagicMock()
            mock_app.logger = mock_logger

            # Call function with expected exception
            with pytest.raises(ValueError):
                get_model_by_name("Unknown")

            # Assert error was logged
            mock_logger.error.assert_called_once_with("Model Unknown not found in registry")
