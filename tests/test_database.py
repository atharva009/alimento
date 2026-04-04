"""
Unit tests for database.py

Test strategy: validate MongoDBManager behaviour when no real database is
available (no MONGODB_URI in environment). These tests are safe to run in CI
without any external services.

Framework: pytest
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestMongoDBManagerNoUri:
    """
    Test case TC-08: MongoDBManager degrades gracefully when MONGODB_URI is absent.

    Input:    MONGODB_URI env var is unset (or empty string)
    Oracle:   client is None, db is None, is_connected() returns False,
              all data-access methods return safe fallback values instead of raising.
    Success:  all assertions pass without exceptions
    Failure:  AttributeError, ConnectionError, or any unhandled exception
    """

    def setup_method(self):
        """Ensure MONGODB_URI is absent for every test in this class."""
        self._original_uri = os.environ.pop("MONGODB_URI", None)
        # Also reset the module-level singleton so each test gets a fresh instance
        import database
        database.db_manager = None

    def teardown_method(self):
        """Restore original env var (if any) after each test."""
        import database
        database.db_manager = None
        if self._original_uri is not None:
            os.environ["MONGODB_URI"] = self._original_uri
        else:
            os.environ.pop("MONGODB_URI", None)

    def test_client_is_none_without_uri(self):
        from database import MongoDBManager
        mgr = MongoDBManager()
        assert mgr.client is None

    def test_db_is_none_without_uri(self):
        from database import MongoDBManager
        mgr = MongoDBManager()
        assert mgr.db is None

    def test_is_connected_returns_false_without_uri(self):
        from database import MongoDBManager
        mgr = MongoDBManager()
        assert mgr.is_connected() is False

    def test_get_history_returns_empty_list_without_uri(self):
        from database import MongoDBManager
        mgr = MongoDBManager()
        result = mgr.get_history()
        assert isinstance(result, list)
        assert result == []

    def test_get_stats_returns_dict_without_uri(self):
        """get_stats should return a dict (possibly with an error key) not raise."""
        from database import MongoDBManager
        mgr = MongoDBManager()
        result = mgr.get_stats()
        assert isinstance(result, dict)

    def test_save_analysis_returns_error_dict_without_uri(self):
        from database import MongoDBManager
        mgr = MongoDBManager()
        result = mgr.save_analysis({"meal": "test"})
        assert isinstance(result, dict)
        assert result.get("success") is False or "error" in result

    def test_delete_analysis_returns_error_dict_without_uri(self):
        from database import MongoDBManager
        mgr = MongoDBManager()
        result = mgr.delete_analysis("507f1f77bcf86cd799439011")
        assert isinstance(result, dict)

    def test_ensure_indexes_returns_false_without_uri(self):
        from database import MongoDBManager
        mgr = MongoDBManager()
        result = mgr.ensure_indexes()
        assert result is False


class TestGetDb:
    """
    Test case TC-09: get_db() returns a singleton MongoDBManager instance.

    Oracle: successive calls to get_db() return the exact same object (is).
    Success: id(first_call) == id(second_call)
    Failure: two different instances created
    """

    def setup_method(self):
        os.environ.pop("MONGODB_URI", None)
        import database
        database.db_manager = None

    def teardown_method(self):
        import database
        database.db_manager = None

    def test_get_db_returns_singleton(self):
        from database import get_db
        first = get_db()
        second = get_db()
        assert first is second

    def test_get_db_returns_mongodb_manager_instance(self):
        from database import get_db, MongoDBManager
        instance = get_db()
        assert isinstance(instance, MongoDBManager)
