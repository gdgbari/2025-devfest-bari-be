"""
Shared pytest configuration and fixtures for all tests
"""


def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line("markers", "unit: Unit tests with mocked dependencies")
