from pydantic import BaseModel, Field, validator
from pathlib import Path
import json
from typing import Optional, Dict, Any
from loguru import logger
import os

class LoggingConfig(BaseModel):
    level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    file: str = Field(default="logs/app.log")
    max_size: int = Field(default=10485760, ge=1024)  # 10MB
    backup_count: int = Field(default=5, ge=1)
    format: str = Field(default="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")

class DatabaseConfig(BaseModel):
    type: str = Field(default="sqlite", pattern="^(sqlite|postgresql|mysql)$")
    path: str = Field(default="data/database.db")
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    database: Optional[str] = None

class SecurityConfig(BaseModel):
    min_password_length: int = Field(default=8, ge=6)
    jwt_secret: str = Field(default="your-secret-key")
    jwt_algorithm: str = Field(default="HS256")
    token_expire_minutes: int = Field(default=30, ge=1)
    salt_rounds: int = Field(default=12, ge=10)

class BackupConfig(BaseModel):
    enabled: bool = Field(default=True)
    max_backups: int = Field(default=5, ge=1)
    backup_dir: str = Field(default="backups")
    schedule: str = Field(default="0 0 * * *")  # Daily at midnight

class AppConfig(BaseModel):
    name: str = Field(default="Smart Shop Manager")
    version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    backup: BackupConfig = Field(default_factory=BackupConfig)

    @validator('database')
    def validate_database_config(cls, v, values):
        if v.type != "sqlite":
            if not all([v.host, v.port, v.username, v.password, v.database]):
                raise ValueError("Database host, port, username, password, and database name are required for non-SQLite databases")
        return v

class ConfigManager:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not ConfigManager._initialized:
            self.config_dir = Path("config")
            self.config_dir.mkdir(exist_ok=True)
            self.config_file = self.config_dir / "config.json"
            self.config = self._load_config()
            ConfigManager._initialized = True
    
    def _load_config(self) -> AppConfig:
        """Load configuration from file or create default if not exists."""
        if not self.config_file.exists():
            return self._create_default_config()
        
        try:
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)
            return AppConfig(**config_data)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> AppConfig:
        """Create default configuration."""
        config = AppConfig()
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config.model_dump(), f, indent=4)
            logger.info("Created default configuration file")
        except Exception as e:
            logger.error(f"Error creating default config: {e}")
        
        return config
    
    def get(self, key: str, default: Any = None) -> Any:
        if not key or not isinstance(key, str):
            raise ValueError("Invalid key format")
        keys = key.split('.')
        value = self.config
        try:
            for k in keys:
                if isinstance(value, dict):
                    value = value[k]
                else:
                    value = getattr(value, k)
            # Type conversion
            if isinstance(value, str):
                if value.isdigit():
                    return int(value)
                try:
                    return float(value)
                except Exception:
                    pass
                if value.lower() in ("true", "false"):
                    return value.lower() == "true"
            return value
        except Exception:
            return default
    
    def set(self, key: str, value: Any) -> bool:
        if not key or not isinstance(key, str):
            raise ValueError("Invalid key format")
        keys = key.split('.')
        d = self.config
        for k in keys[:-1]:
            if isinstance(d, dict):
                if k not in d:
                    d[k] = {}
                d = d[k]
            else:
                if not hasattr(d, k):
                    setattr(d, k, {})
                d = getattr(d, k)
        if isinstance(d, dict):
            d[keys[-1]] = value
        else:
            setattr(d, keys[-1], value)
        return True
    
    def _save_config(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config.model_dump(), f, indent=4)
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def get_all(self) -> dict:
        if hasattr(self.config, 'model_dump'):
            return self.config.model_dump()
        return dict(self.config)
    
    def update(self, new_config: dict) -> bool:
        def deep_update(d, u):
            for k, v in u.items():
                if isinstance(v, dict):
                    d[k] = deep_update(d.get(k, {}), v)
                else:
                    d[k] = v
            return d
        if isinstance(self.config, dict):
            self.config = deep_update(self.config, new_config)
        else:
            for k, v in new_config.items():
                setattr(self.config, k, v)
        self._save_config()
        return True
    
    def reset_to_default(self) -> bool:
        self.config = self._create_default_config()
        self._save_config()
        return True
    
    def validate_config(self) -> tuple[bool, list[str]]:
        """Validate the current configuration."""
        try:
            self.config = AppConfig(**self.config.model_dump())
            return True, []
        except Exception as e:
            return False, [str(e)]

    def load_config(self, config):
        self.config = config

# Singleton instance for easy import
config_manager = ConfigManager() 