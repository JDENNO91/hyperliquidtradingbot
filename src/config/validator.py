"""
Configuration Validator

This module provides comprehensive validation for trading system configurations.
Supports both programmatic validation and JSON Schema validation.
"""

import json
import os
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import logging

try:
    import jsonschema
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    jsonschema = None

logger = logging.getLogger(__name__)


@dataclass
class ValidationError:
    """Represents a configuration validation error."""
    field: str
    message: str
    severity: str  # 'error', 'warning', 'info'
    suggested_value: Optional[Any] = None


class ConfigValidationError(Exception):
    """Exception raised when configuration validation fails."""
    
    def __init__(self, message: str, errors: List[ValidationError] = None):
        super().__init__(message)
        self.errors = errors or []


class ConfigValidator:
    """Configuration validator for trading system."""
    
    def __init__(self, use_schema: bool = True):
        """
        Initialize validator.
        
        Args:
            use_schema: Whether to use JSON Schema validation (requires jsonschema package)
        """
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []
        self.info: List[ValidationError] = []
        self.use_schema = use_schema and JSONSCHEMA_AVAILABLE
        self.schema = None
        
        if self.use_schema:
            self._load_schema()
    
    def _load_schema(self):
        """Load JSON schema for validation."""
        try:
            schema_path = Path(__file__).parent / "config_schema.json"
            if schema_path.exists():
                with open(schema_path, 'r') as f:
                    self.schema = json.load(f)
                logger.debug("JSON Schema loaded successfully")
            else:
                logger.warning(f"Schema file not found: {schema_path}")
                self.use_schema = False
        except Exception as e:
            logger.warning(f"Failed to load JSON schema: {e}")
            self.use_schema = False
    
    def validate(self, config: Dict[str, Any]) -> Tuple[bool, List[ValidationError]]:
        """Validate a configuration dictionary."""
        self.errors.clear()
        self.warnings.clear()
        self.info.clear()
        
        # JSON Schema validation (if available)
        if self.use_schema and self.schema:
            self._validate_with_schema(config)
        
        # Programmatic validation
        self._validate_required_fields(config)
        self._validate_data_types(config)
        self._validate_ranges(config)
        self._validate_business_logic(config)
        
        all_issues = self.errors + self.warnings + self.info
        is_valid = len(self.errors) == 0
        
        return is_valid, all_issues
    
    def _validate_with_schema(self, config: Dict[str, Any]):
        """Validate configuration using JSON Schema."""
        try:
            jsonschema.validate(instance=config, schema=self.schema)
        except jsonschema.ValidationError as e:
            # Extract field path from error
            field_path = '.'.join(str(p) for p in e.absolute_path) if e.absolute_path else 'root'
            self.errors.append(ValidationError(
                field=field_path,
                message=e.message,
                severity='error',
                suggested_value=e.validator_value if hasattr(e, 'validator_value') else None
            ))
        except jsonschema.SchemaError as e:
            logger.error(f"JSON Schema error: {e}")
            self.errors.append(ValidationError(
                field='schema',
                message=f"Schema validation error: {e}",
                severity='error'
            ))
    
    def _validate_required_fields(self, config: Dict[str, Any]):
        """Validate required fields are present."""
        required_fields = ['strategy', 'trading', 'indicators']
        
        for field in required_fields:
            if field not in config:
                self.errors.append(ValidationError(
                    field=field,
                    message=f"Required field '{field}' is missing",
                    severity='error'
                ))
    
    def _validate_data_types(self, config: Dict[str, Any]):
        """Validate data types."""
        if 'strategy' in config and not isinstance(config['strategy'], str):
            self.errors.append(ValidationError(
                field='strategy',
                message='Strategy must be a string',
                severity='error'
            ))
        
        if 'trading' in config and not isinstance(config['trading'], dict):
            self.errors.append(ValidationError(
                field='trading',
                message='Trading config must be a dictionary',
                severity='error'
            ))
    
    def _validate_ranges(self, config: Dict[str, Any]):
        """Validate value ranges."""
        if 'trading' in config:
            trading = config['trading']
            
            if 'leverage' in trading:
                leverage = trading['leverage']
                if not (1 <= leverage <= 50):
                    self.errors.append(ValidationError(
                        field='trading.leverage',
                        message='Leverage must be between 1 and 50',
                        severity='error'
                    ))
            
            if 'positionSize' in trading:
                size = trading['positionSize']
                if not (0.001 <= size <= 1.0):
                    self.errors.append(ValidationError(
                        field='trading.positionSize',
                        message='Position size must be between 0.001 and 1.0',
                        severity='error'
                    ))
    
    def _validate_business_logic(self, config: Dict[str, Any]):
        """Validate business logic rules."""
        if 'indicators' in config and 'rsi' in config['indicators']:
            rsi = config['indicators']['rsi']
            if 'overbought' in rsi and 'oversold' in rsi:
                if rsi['overbought'] <= rsi['oversold']:
                    self.errors.append(ValidationError(
                        field='indicators.rsi.overbought',
                        message='RSI overbought must be greater than oversold',
                        severity='error'
                    ))
    
    def validate_file(self, config_path: str) -> Tuple[bool, List[ValidationError]]:
        """Validate a configuration file."""
        if not os.path.exists(config_path):
            return False, [ValidationError(
                field='file',
                message=f'Configuration file not found: {config_path}',
                severity='error'
            )]
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            return self.validate(config)
        except json.JSONDecodeError as e:
            return False, [ValidationError(
                field='file',
                message=f'Invalid JSON: {e}',
                severity='error'
            )]
        except Exception as e:
            return False, [ValidationError(
                field='file',
                message=f'Error reading file: {e}',
                severity='error'
            )]


def validate_config_file(config_path: str) -> Tuple[bool, str]:
    """Convenience function to validate a configuration file."""
    validator = ConfigValidator()
    is_valid, issues = validator.validate_file(config_path)
    
    if not issues:
        return True, "✅ Configuration is valid!"
    
    report = ["Configuration Validation Report", "=" * 40]
    
    errors = [i for i in issues if i.severity == 'error']
    warnings = [i for i in issues if i.severity == 'warning']
    
    if errors:
        report.append(f"\n❌ ERRORS ({len(errors)}):")
        for error in errors:
            report.append(f"  • {error.field}: {error.message}")
    
    if warnings:
        report.append(f"\n⚠️  WARNINGS ({len(warnings)}):")
        for warning in warnings:
            report.append(f"  • {warning.field}: {warning.message}")
    
    return is_valid, "\n".join(report)