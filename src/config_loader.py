import json
import os
from typing import Dict, Any, Optional


class ConfigLoader:
    """Load and validate configuration from JSON file."""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        
    def load(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
        
        self._validate()
        return self.config
    
    def _validate(self) -> None:
        """Validate required configuration fields."""
        required_sections = ['general', 'hash', 'input', 'output']
        
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required configuration section: {section}")
        
        if self.config['general']['worker_count'] < 1:
            raise ValueError("worker_count must be at least 1")
        
        if self.config['general']['chunk_size'] < 1:
            raise ValueError("chunk_size must be at least 1")
        
        valid_algorithms = ['SHA256', 'SHA384', 'SHA512', 'PBKDF2']
        if self.config['hash']['algorithm'] not in valid_algorithms:
            raise ValueError(f"Invalid hash algorithm. Must be one of: {valid_algorithms}")
    
    def get(self, *keys: str, default: Any = None) -> Any:
        """Get nested configuration value."""
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def set(self, value: Any, *keys: str) -> None:
        """Set nested configuration value."""
        if not keys:
            return
        
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
    
    def save(self, path: Optional[str] = None) -> None:
        """Save configuration to file."""
        save_path = path or self.config_path
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
