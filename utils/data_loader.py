"""
Data Loader Utility
"""

import csv
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from config.settings import settings


@dataclass
class TestDataRecord:
    """Represents a single test data record."""

    data: Dict[str, Any]
    source_file: str
    record_index: int

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from data with optional default."""
        return self.data.get(key, default)

    def __getitem__(self, key: str) -> Any:
        return self.data[key]

    def __contains__(self, key: str) -> bool:
        return key in self.data


class DataLoader:
    """
    Loads test data from various file formats.
    Supports JSON, CSV, and YAML files.
    """

    def __init__(self, data_dir: Path = None, logger: logging.Logger = None):
        self.data_dir = data_dir or settings.DATA_DIR
        self.logger = logger or logging.getLogger(__name__)
        self._cache: Dict[str, Any] = {}

    def _resolve_path(self, filename: str) -> Path:
        """Resolve file path, checking data directory if not absolute."""
        path = Path(filename)
        if path.is_absolute():
            return path
        return self.data_dir / filename

    def load_json(self, filename: str, use_cache: bool = True) -> Union[Dict, List]:
        """
        Load data from a JSON file.

        Args:
            filename: Path to JSON file (relative to data_dir or absolute)
            use_cache: Whether to use cached data

        Returns:
            Parsed JSON data (dict or list)
        """
        filepath = self._resolve_path(filename)
        cache_key = f"json:{filepath}"

        if use_cache and cache_key in self._cache:
            self.logger.debug(f"Using cached JSON data: {filepath}")
            return self._cache[cache_key]

        self.logger.info(f"Loading JSON file: {filepath}")

        if not filepath.exists():
            raise FileNotFoundError(f"JSON file not found: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        if use_cache:
            self._cache[cache_key] = data

        return data

    def load_csv(
        self, filename: str, delimiter: str = ",", use_cache: bool = True
    ) -> List[Dict[str, str]]:
        """
        Load data from a CSV file.

        Args:
            filename: Path to CSV file
            delimiter: Field delimiter
            use_cache: Whether to use cached data

        Returns:
            List of dictionaries (one per row)
        """
        filepath = self._resolve_path(filename)
        cache_key = f"csv:{filepath}"

        if use_cache and cache_key in self._cache:
            self.logger.debug(f"Using cached CSV data: {filepath}")
            return self._cache[cache_key]

        self.logger.info(f"Loading CSV file: {filepath}")

        if not filepath.exists():
            raise FileNotFoundError(f"CSV file not found: {filepath}")

        data = []
        with open(filepath, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            data = list(reader)

        if use_cache:
            self._cache[cache_key] = data

        return data

    def load_yaml(self, filename: str, use_cache: bool = True) -> Union[Dict, List]:
        """
        Load data from a YAML file.

        Args:
            filename: Path to YAML file
            use_cache: Whether to use cached data

        Returns:
            Parsed YAML data
        """
        try:
            import yaml
        except ImportError:
            raise ImportError(
                "PyYAML is required for YAML support. Install with: pip install pyyaml"
            )

        filepath = self._resolve_path(filename)
        cache_key = f"yaml:{filepath}"

        if use_cache and cache_key in self._cache:
            self.logger.debug(f"Using cached YAML data: {filepath}")
            return self._cache[cache_key]

        self.logger.info(f"Loading YAML file: {filepath}")

        if not filepath.exists():
            raise FileNotFoundError(f"YAML file not found: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if use_cache:
            self._cache[cache_key] = data

        return data

    def load(self, filename: str, use_cache: bool = True) -> Union[Dict, List]:
        """
        Load data from file, automatically detecting format by extension.

        Args:
            filename: Path to data file
            use_cache: Whether to use cached data

        Returns:
            Parsed data
        """
        filepath = self._resolve_path(filename)
        extension = filepath.suffix.lower()

        match extension:
            case ".json":
                return self.load_json(filename, use_cache)
            case ".csv" | ".tsv":
                delimiter = "\t" if extension == ".tsv" else ","
                return self.load_csv(filename, delimiter, use_cache)
            case ".yaml" | ".yml":
                return self.load_yaml(filename, use_cache)
            case _:
                raise ValueError(f"Unsupported file format: {extension}")

    def load_test_data(
        self, filename: str, use_cache: bool = True
    ) -> List[TestDataRecord]:
        """
        Load test data as TestDataRecord objects.

        Args:
            filename: Path to data file
            use_cache: Whether to use cached data

        Returns:
            List of TestDataRecord objects
        """
        raw_data = self.load(filename, use_cache)

        # Ensure data is a list
        if isinstance(raw_data, dict):
            if "test_data" in raw_data:
                raw_data = raw_data["test_data"]
            else:
                raw_data = [raw_data]

        filepath = str(self._resolve_path(filename))

        return [
            TestDataRecord(data=record, source_file=filepath, record_index=idx)
            for idx, record in enumerate(raw_data)
        ]

    def get_parameterized_data(
        self, filename: str, param_keys: List[str] = None
    ) -> List[tuple]:
        """
        Get data formatted for pytest parametrize.

        Args:
            filename: Path to data file
            param_keys: List of keys to extract (uses all if not provided)

        Returns:
            List of tuples for parametrize
        """
        records = self.load_test_data(filename)

        if not records:
            return []

        if param_keys is None:
            param_keys = list(records[0].data.keys())

        return [tuple(record.get(key) for key in param_keys) for record in records]

    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._cache.clear()
        self.logger.debug("Data cache cleared")

    def save_json(
        self, data: Union[Dict, List], filename: str, indent: int = 2
    ) -> Path:
        """
        Save data to a JSON file.

        Args:
            data: Data to save
            filename: Output filename
            indent: JSON indentation

        Returns:
            Path to saved file
        """
        filepath = self._resolve_path(filename)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)

        self.logger.info(f"Saved JSON data to: {filepath}")
        return filepath


# Global data loader instance
_data_loader: Optional[DataLoader] = None


def get_data_loader() -> DataLoader:
    """Get or create global data loader instance."""
    global _data_loader
    if _data_loader is None:
        _data_loader = DataLoader()
    return _data_loader


def load_test_data(filename: str) -> List[TestDataRecord]:
    """Convenience function to load test data."""
    return get_data_loader().load_test_data(filename)


def load_json(filename: str) -> Union[Dict, List]:
    """Convenience function to load JSON data."""
    return get_data_loader().load_json(filename)


def load_csv(filename: str) -> List[Dict[str, str]]:
    """Convenience function to load CSV data."""
    return get_data_loader().load_csv(filename)
