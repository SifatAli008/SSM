import os
from pathlib import Path
import sqlite3
import logging
from datetime import datetime
from typing import List, Optional
import json

logger = logging.getLogger(__name__)

class Migration:
    def __init__(self, version: int, name: str):
        self.version = version
        self.name = name
        self.created_at = datetime.utcnow()
    
    def up(self, connection: sqlite3.Connection):
        """Apply the migration."""
        raise NotImplementedError
    
    def down(self, connection: sqlite3.Connection):
        """Revert the migration."""
        raise NotImplementedError

class MigrationManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.migrations_dir = Path("app/migrations")
        self.migrations_dir.mkdir(exist_ok=True)
        self._ensure_migrations_table()
    
    def _ensure_migrations_table(self):
        """Create migrations table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS migrations (
                    version INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    def get_applied_migrations(self) -> List[int]:
        """Get list of applied migration versions."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT version FROM migrations ORDER BY version")
            return [row[0] for row in cursor.fetchall()]
    
    def get_pending_migrations(self) -> List[Migration]:
        """Get list of pending migrations."""
        applied = set(self.get_applied_migrations())
        pending = []
        
        for file in sorted(self.migrations_dir.glob("*.py")):
            if file.stem.startswith("migration_"):
                version = int(file.stem.split("_")[1])
                if version not in applied:
                    module = self._load_migration_module(file)
                    if module:
                        pending.append(module.Migration(version, file.stem))
        
        return sorted(pending, key=lambda m: m.version)
    
    def _load_migration_module(self, file_path: Path) -> Optional[type]:
        """Load a migration module."""
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(file_path.stem, str(file_path))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            logger.error(f"Failed to load migration {file_path}: {e}")
            return None
    
    def apply_migrations(self, target_version: Optional[int] = None):
        """Apply pending migrations up to target version."""
        pending = self.get_pending_migrations()
        if target_version is not None:
            pending = [m for m in pending if m.version <= target_version]
        
        with sqlite3.connect(self.db_path) as conn:
            for migration in pending:
                try:
                    logger.info(f"Applying migration {migration.version}: {migration.name}")
                    migration.up(conn)
                    conn.execute(
                        "INSERT INTO migrations (version, name) VALUES (?, ?)",
                        (migration.version, migration.name)
                    )
                    conn.commit()
                    logger.info(f"Successfully applied migration {migration.version}")
                except Exception as e:
                    conn.rollback()
                    logger.error(f"Failed to apply migration {migration.version}: {e}")
                    raise
    
    def rollback_migrations(self, target_version: Optional[int] = None):
        """Rollback migrations down to target version."""
        applied = self.get_applied_migrations()
        if target_version is not None:
            applied = [v for v in applied if v > target_version]
        
        with sqlite3.connect(self.db_path) as conn:
            for version in reversed(applied):
                try:
                    migration_file = self.migrations_dir / f"migration_{version}.py"
                    if migration_file.exists():
                        module = self._load_migration_module(migration_file)
                        if module:
                            logger.info(f"Rolling back migration {version}")
                            module.Migration(version, migration_file.stem).down(conn)
                            conn.execute("DELETE FROM migrations WHERE version = ?", (version,))
                            conn.commit()
                            logger.info(f"Successfully rolled back migration {version}")
                except Exception as e:
                    conn.rollback()
                    logger.error(f"Failed to rollback migration {version}: {e}")
                    raise
    
    def create_migration(self, name: str) -> Path:
        """Create a new migration file."""
        applied = self.get_applied_migrations()
        next_version = max(applied, default=0) + 1
        
        template = f'''import sqlite3
from app.utils.migrations import Migration

class Migration(Migration):
    def __init__(self, version: int, name: str):
        super().__init__(version, name)
    
    def up(self, connection: sqlite3.Connection):
        """Apply the migration."""
        # TODO: Implement migration
        pass
    
    def down(self, connection: sqlite3.Connection):
        """Revert the migration."""
        # TODO: Implement rollback
        pass
'''
        
        file_path = self.migrations_dir / f"migration_{next_version}_{name}.py"
        file_path.write_text(template)
        logger.info(f"Created migration file: {file_path}")
        return file_path 