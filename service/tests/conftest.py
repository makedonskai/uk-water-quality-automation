"""Shared pytest fixtures for the test suite."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db import Base


@pytest.fixture
def in_memory_db():
    """Create a fresh in-memory SQLite database for each test."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    test_session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    yield test_session_factory  # tests use this; runs once per test
    engine.dispose()  # cleanup after the test
