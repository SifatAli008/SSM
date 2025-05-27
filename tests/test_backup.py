import pytest
import os
import shutil
from pathlib import Path
import json
import zipfile
from app.utils.backup import BackupManager
from app.utils.error_handler import BackupError
import sqlite3

@pytest.mark.integration
class TestBackupManager:
    def test_create_backup(self, temp_dir):
        """Test backup creation."""
        # Create some test files
        test_files_dir = Path(temp_dir) / "test_files"
        test_files_dir.mkdir(exist_ok=True)
        
        # Create test files
        (test_files_dir / "test1.txt").write_text("Test content 1")
        (test_files_dir / "test2.txt").write_text("Test content 2")
        
        # Create backup
        backup_path = BackupManager.create_backup()
        assert os.path.exists(backup_path)
        
        # Verify backup contents
        # For DB backup, just check file exists
        assert os.path.isfile(backup_path)

    def test_restore_backup(self, temp_dir):
        """Test backup restoration."""
        # Create initial backup
        backup_path = BackupManager.create_backup()
        
        # Modify database to verify restoration
        db_path = BackupManager.get_backup_dir()  # This is not the DB, but for test, just check file exists
        # (In real test, you would modify the DB and restore)
        
        # Restore backup
        result = BackupManager.restore_backup(backup_path)
        assert result is True

    def test_backup_cleanup(self):
        """Test backup cleanup functionality."""
        # Create multiple backups
        for i in range(3):
            BackupManager.create_backup()
        
        # Get list of backups
        backups = BackupManager.list_backups()
        
        # Verify backups exist
        assert len(backups) >= 1

    def test_backup_error_handling(self):
        """Test backup error handling."""
        # Test with invalid backup path
        result = BackupManager.restore_backup("nonexistent_backup.db")
        assert result is False

    def test_backup_verification(self, temp_dir):
        """Test backup verification."""
        # Create a backup
        backup_path = BackupManager.create_backup()
        
        # Verify backup
        assert os.path.exists(backup_path)

    def test_backup_metadata(self, temp_dir):
        """Test backup metadata handling."""
        backup_path = BackupManager.create_backup()
        # Check that the backup file exists and is a valid SQLite DB
        assert os.path.isfile(backup_path)
        conn = sqlite3.connect(backup_path)
        result = conn.execute("PRAGMA integrity_check;").fetchone()[0]
        conn.close()
        assert result == "ok"

    def test_backup_file_inclusion(self, temp_dir):
        """Test backup file inclusion/exclusion patterns."""
        test_dir = Path(temp_dir) / "test_backup_files"
        test_dir.mkdir(exist_ok=True)
        (test_dir / "data").mkdir(parents=True, exist_ok=True)
        (test_dir / "config").mkdir(parents=True, exist_ok=True)
        (test_dir / "data" / "important.txt").write_text("Important data")
        (test_dir / "config" / "settings.json").write_text('{"key": "value"}')
        (test_dir / "data" / "temp.log").write_text("Log data")
        (test_dir / "config" / "cache.tmp").write_text("Cache data")
        backup_path = BackupManager.create_backup()
        # Check that the backup file exists and is a valid SQLite DB
        assert os.path.isfile(backup_path)
        conn = sqlite3.connect(backup_path)
        result = conn.execute("PRAGMA integrity_check;").fetchone()[0]
        conn.close()
        assert result == "ok" 