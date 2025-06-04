import os
import shutil
from datetime import datetime
from pathlib import Path
from threading import Thread, Event
import time
from typing import Optional, List
from app.utils.logger import Logger
from app.utils.config_manager import config_manager
from app.utils.database import DatabaseManager
from app.core.event_system import EventSystem, EventTypes

logger = Logger()

class BackupManager:
    def __init__(self, event_system: EventSystem):
        self.event_system = event_system
        self._stop_event = Event()
        self._backup_thread = None
        self._setup_backup_directory()
    
    def _setup_backup_directory(self):
        """Set up backup directory if it doesn't exist."""
        backup_dir = Path(config_manager.get('backup.backup_dir'))
        backup_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Backup directory set up: {backup_dir}")
    
    def start_auto_backup(self):
        """Start automatic backup thread."""
        if self._backup_thread is None or not self._backup_thread.is_alive():
            self._stop_event.clear()
            self._backup_thread = Thread(target=self._auto_backup_loop, daemon=True)
            self._backup_thread.start()
            logger.info("Automatic backup started")
    
    def stop_auto_backup(self):
        """Stop automatic backup thread."""
        if self._backup_thread and self._backup_thread.is_alive():
            self._stop_event.set()
            self._backup_thread.join()
            logger.info("Automatic backup stopped")
    
    def _auto_backup_loop(self):
        """Automatic backup loop."""
        while not self._stop_event.is_set():
            try:
                # Get backup schedule from config
                schedule = config_manager.get('backup.schedule')
                if schedule:
                    # Parse schedule (cron format)
                    # For now, just backup daily
                    time.sleep(24 * 60 * 60)  # Sleep for 24 hours
                    self.create_backup()
            except Exception as e:
                logger.error(f"Error in auto backup loop: {e}")
                time.sleep(60)  # Sleep for 1 minute on error
    
    def create_backup(self) -> Optional[str]:
        """Create a new backup."""
        try:
            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = Path(config_manager.get('backup.backup_dir'))
            backup_file = backup_dir / f"backup_{timestamp}.db"
            
            # Create backup
            if DatabaseManager().backup_database(str(backup_file)):
                # Clean up old backups
                self._cleanup_old_backups()
                
                # Publish backup event
                self.event_system.publish(EventTypes.SYSTEM_BACKUP, {
                    'backup_file': str(backup_file),
                    'timestamp': timestamp
                })
                
                logger.info(f"Backup created: {backup_file}")
                return str(backup_file)
            return None
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return None
    
    def restore_backup(self, backup_file: str) -> bool:
        """Restore from a backup file."""
        try:
            if DatabaseManager().restore_database(backup_file):
                # Publish restore event
                self.event_system.publish(EventTypes.SYSTEM_RESTORE, {
                    'backup_file': backup_file,
                    'timestamp': datetime.now().isoformat()
                })
                
                logger.info(f"Backup restored from: {backup_file}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            return False
    
    def _cleanup_old_backups(self):
        """Clean up old backups based on retention policy."""
        try:
            backup_dir = Path(config_manager.get('backup.backup_dir'))
            max_backups = config_manager.get('backup.max_backups')
            
            # Get all backup files
            backup_files = sorted(
                backup_dir.glob("backup_*.db"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            # Remove excess backups
            for backup_file in backup_files[max_backups:]:
                backup_file.unlink()
                logger.info(f"Removed old backup: {backup_file}")
        except Exception as e:
            logger.error(f"Failed to cleanup old backups: {e}")
    
    def list_backups(self) -> List[dict]:
        """List all available backups."""
        try:
            backup_dir = Path(config_manager.get('backup.backup_dir'))
            backups = []
            
            for backup_file in backup_dir.glob("backup_*.db"):
                stat = backup_file.stat()
                backups.append({
                    'filename': backup_file.name,
                    'path': str(backup_file),
                    'size': stat.st_size,
                    'created_at': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
            
            return sorted(backups, key=lambda x: x['created_at'], reverse=True)
        except Exception as e:
            logger.error(f"Failed to list backups: {e}")
            return []
    
    def get_backup_info(self, backup_file: str) -> Optional[dict]:
        """Get information about a specific backup."""
        try:
            backup_path = Path(backup_file)
            if not backup_path.exists():
                return None
            
            stat = backup_path.stat()
            return {
                'filename': backup_path.name,
                'path': str(backup_path),
                'size': stat.st_size,
                'created_at': datetime.fromtimestamp(stat.st_mtime).isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get backup info: {e}")
            return None 