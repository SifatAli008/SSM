import pytest
import os
import shutil
from pathlib import Path
import json
import zipfile
from app.utils.backup import BackupManager
from app.utils.error_handler import BackupError

@pytest.mark.integration
class TestBackupManager:
    def test_create_backup(self, backup_manager, temp_dir):
        """Test backup creation."""
        # Create some test files
        test_files_dir = Path(temp_dir) / "test_files"
        test_files_dir.mkdir(exist_ok=True)
        
        # Create test files
        (test_files_dir / "test1.txt").write_text("Test content 1")
        (test_files_dir / "test2.txt").write_text("Test content 2")
        
        # Create backup
        backup_path = backup_manager.create_backup("Test backup")
        assert os.path.exists(backup_path)
        
        # Verify backup contents
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            # Check metadata
            assert 'metadata.json' in zipf.namelist()
            with zipf.open('metadata.json') as f:
                metadata = json.load(f)
                assert metadata['description'] == "Test backup"
                assert 'database.sqlite' in metadata['files']
            
            # Check database backup
            assert 'database.sqlite' in zipf.namelist()
    
    def test_restore_backup(self, backup_manager, temp_dir):
        """Test backup restoration."""
        # Create initial backup
        backup_path = backup_manager.create_backup("Test backup for restoration")
        
        # Modify database to verify restoration
        with backup_manager.db_path.open('w') as f:
            f.write("Modified content")
        
        # Restore backup
        backup_manager.restore_backup(backup_path)
        
        # Verify restoration
        assert backup_manager.db_path.exists()
    
    def test_backup_cleanup(self, backup_manager):
        """Test backup cleanup functionality."""
        # Create multiple backups
        for i in range(5):
            backup_manager.create_backup(f"Test backup {i}")
        
        # Get list of backups
        backups = backup_manager.list_backups()
        
        # Verify only the most recent backups are kept
        max_backups = backup_manager.config.get("backup", {}).get("max_backups", 3)
        assert len(backups) <= max_backups
    
    def test_backup_verification(self, backup_manager, temp_dir):
        """Test backup verification."""
        # Create a backup
        backup_path = backup_manager.create_backup("Test backup")
        
        # Verify backup
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            assert 'metadata.json' in zipf.namelist()
            assert 'database.sqlite' in zipf.namelist()
    
    def test_backup_error_handling(self, backup_manager):
        """Test backup error handling."""
        # Test with invalid backup path
        with pytest.raises(FileNotFoundError):
            backup_manager.restore_backup("nonexistent_backup.zip")
        
        # Test with corrupted backup
        invalid_backup = Path(backup_manager.backup_dir) / "invalid_backup.zip"
        invalid_backup.write_text("Invalid backup content")
        
        with pytest.raises(BackupError):
            backup_manager.restore_backup(str(invalid_backup))
    
    def test_backup_metadata(self, backup_manager):
        """Test backup metadata handling."""
        # Create backup with description
        description = "Test backup with metadata"
        backup_path = backup_manager.create_backup(description)
        
        # Verify metadata
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            with zipf.open('metadata.json') as f:
                metadata = json.load(f)
                assert metadata['description'] == description
                assert 'timestamp' in metadata
                assert 'database_path' in metadata
                assert 'files' in metadata
    
    def test_backup_file_inclusion(self, backup_manager, temp_dir):
        """Test backup file inclusion/exclusion patterns."""
        # Create test files
        test_dir = Path(temp_dir) / "test_backup_files"
        test_dir.mkdir(exist_ok=True)
        
        # Create files that should be included
        (test_dir / "data" / "important.txt").write_text("Important data")
        (test_dir / "config" / "settings.json").write_text('{"key": "value"}')
        
        # Create files that should be excluded
        (test_dir / "data" / "temp.log").write_text("Log data")
        (test_dir / "config" / "cache.tmp").write_text("Cache data")
        
        # Create backup
        backup_path = backup_manager.create_backup("Test file inclusion")
        
        # Verify backup contents
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            files = zipf.namelist()
            assert any('important.txt' in f for f in files)
            assert any('settings.json' in f for f in files)
            assert not any('temp.log' in f for f in files)
            assert not any('cache.tmp' in f for f in files) 