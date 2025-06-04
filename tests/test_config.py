import pytest
import json
from pathlib import Path
from app.utils.config_manager import ConfigManager
from app.utils.error_handler import ConfigurationError

class TestConfigManager:
    def test_config_initialization(self, config_manager, test_config):
        """Test configuration initialization."""
        assert config_manager.get("app.name") == test_config["app"]["name"]
        assert config_manager.get("app.version") == test_config["app"]["version"]
        assert config_manager.get("database.type") == test_config["database"]["type"]
    
    def test_config_get_set(self, config_manager):
        """Test getting and setting configuration values."""
        # Test setting new value
        config_manager.set("test.key", "value")
        assert config_manager.get("test.key") == "value"
        
        # Test setting nested value
        config_manager.set("test.nested.key", "nested_value")
        assert config_manager.get("test.nested.key") == "nested_value"
        
        # Test getting non-existent value
        assert config_manager.get("nonexistent.key") is None
        assert config_manager.get("nonexistent.key", "default") == "default"
    
    def test_config_update(self, config_manager):
        """Test updating multiple configuration values."""
        new_config = {
            "app": {
                "name": "Updated Name",
                "version": "2.0.0"
            },
            "new_section": {
                "key": "value"
            }
        }
        
        config_manager.update(new_config)
        
        assert config_manager.get("app.name") == "Updated Name"
        assert config_manager.get("app.version") == "2.0.0"
        assert config_manager.get("new_section.key") == "value"
    
    def test_config_validation(self, config_manager):
        """Test configuration validation."""
        # Test valid configuration
        is_valid, errors = config_manager.validate_config()
        assert is_valid
        assert len(errors) == 0
        
        # Test invalid configuration
        config_manager.set("security.min_password_length", 4)
        is_valid, errors = config_manager.validate_config()
        assert not is_valid
        assert any("password length" in error for error in errors)
        
        # Test missing required field
        config_manager.set("app.name", None)
        is_valid, errors = config_manager.validate_config()
        assert not is_valid
        assert any("Missing required field: app.name" in error for error in errors)
    
    def test_config_reset(self, config_manager, test_config):
        """Test resetting configuration to default values."""
        # Modify configuration
        config_manager.set("app.name", "Modified Name")
        assert config_manager.get("app.name") == "Modified Name"
        
        # Reset configuration
        config_manager.reset_to_default()
        # After reset, expect the default value
        assert config_manager.get("app.name") == "Smart Shop Manager"
    
    def test_config_persistence(self, config_manager, temp_dir):
        """Test configuration persistence to file."""
        # Set new value
        config_manager.set("test.key", "persistent_value")
        
        # Create new instance to load from file
        new_manager = ConfigManager()
        assert new_manager.get("test.key") == "persistent_value"
    
    def test_config_error_handling(self, config_manager):
        """Test configuration error handling."""
        # Test invalid key format
        with pytest.raises(ValueError):
            config_manager.get("invalid..key")
        
        with pytest.raises(ValueError):
            config_manager.set("invalid..key", "value")
        
        # Test invalid value type
        with pytest.raises(ConfigurationError):
            config_manager.set("security.min_password_length", "invalid")
    
    def test_config_section_management(self, config_manager):
        """Test managing configuration sections."""
        # Add new section
        config_manager.set("new_section.key1", "value1")
        config_manager.set("new_section.key2", "value2")
        
        # Verify section
        assert config_manager.get("new_section.key1") == "value1"
        assert config_manager.get("new_section.key2") == "value2"
        
        # Remove section
        config_manager.set("new_section", None)
        assert config_manager.get("new_section.key1") is None
        assert config_manager.get("new_section.key2") is None
    
    def test_config_type_conversion(self, config_manager):
        """Test configuration value type conversion."""
        # Test integer
        config_manager.set("test.int", "123")
        assert isinstance(config_manager.get("test.int"), int)
        assert config_manager.get("test.int") == 123
        
        # Test float
        config_manager.set("test.float", "123.45")
        assert isinstance(config_manager.get("test.float"), float)
        assert config_manager.get("test.float") == 123.45
        
        # Test boolean
        config_manager.set("test.bool", "true")
        assert isinstance(config_manager.get("test.bool"), bool)
        assert config_manager.get("test.bool") is True
        
        # Test list
        config_manager.set("test.list", ["item1", "item2"])
        assert isinstance(config_manager.get("test.list"), list)
        assert config_manager.get("test.list") == ["item1", "item2"]
        
        # Test dict
        config_manager.set("test.dict", {"key": "value"})
        assert isinstance(config_manager.get("test.dict"), dict)
        assert config_manager.get("test.dict") == {"key": "value"} 