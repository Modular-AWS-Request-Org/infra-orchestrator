#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml


PROJECT_NAME_RE = re.compile(r"^[a-z][a-z0-9-]{2,39}$")
ALLOWED_REGIONS = {
    "us-east-1",
    "us-east-2",
    "us-west-1",
    "us-west-2",
    "eu-west-1",
}
SERVICE_TYPES = {
    "frontend": "s3-cloudfront",
    "database": "dynamodb",
    "storage": "s3",
    "compute": "lambda",
}
ALLOWED_SERVICE_KEYS = {"type", "config"}
ALLOWED_CONFIG_KEYS = {
    "frontend": {"index_document", "error_document", "price_class"},
    "database": {
        "billing_mode",
        "hash_key",
        "hash_key_type",
        "range_key",
        "range_key_type",
        "enable_point_in_time_recovery",
    },
    "storage": {"versioning", "encryption"},
    "compute": {"runtime", "memory_size", "timeout", "create_function_url"},
}


def fail(message: str) -> None:
    print(f"Config invalid: {message}", file=sys.stderr)
    raise SystemExit(1)


def ensure_mapping(path: str, value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        fail(f"{path} must be a mapping")
    return value


def ensure_non_empty_string(path: str, value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        fail(f"{path} must be a non-empty string")
    return value


def ensure_optional_string(path: str, value: Any) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        fail(f"{path} must be a string")
    return value


def ensure_bool(path: str, value: Any) -> bool:
    if not isinstance(value, bool):
        fail(f"{path} must be a boolean")
    return value


def ensure_int_range(path: str, value: Any, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        fail(f"{path} must be an integer")
    if not minimum <= value <= maximum:
        fail(f"{path} must be between {minimum} and {maximum}")
    return value


def ensure_enum(path: str, value: Any, allowed: set[str]) -> str:
    if value not in allowed:
        choices = ", ".join(sorted(allowed))
        fail(f"{path} must be one of: {choices}")
    return value


def reject_unknown_keys(path: str, value: dict[str, Any], allowed: set[str]) -> None:
    unknown_keys = sorted(set(value) - allowed)
    if unknown_keys:
        fail(f"{path} contains unsupported keys: {', '.join(unknown_keys)}")


def validate_tags(tags: Any) -> None:
    if tags is None:
        return
    if not isinstance(tags, dict):
        fail("project.tags must be a mapping of string keys to string values")
    for key, value in tags.items():
        if not isinstance(key, str) or not isinstance(value, str):
            fail("project.tags must only contain string keys and string values")


def validate_frontend(config: dict[str, Any]) -> None:
    reject_unknown_keys(
        "services.frontend.config", config, ALLOWED_CONFIG_KEYS["frontend"]
    )
    ensure_non_empty_string(
        "services.frontend.config.index_document", config.get("index_document")
    )
    ensure_non_empty_string(
        "services.frontend.config.error_document", config.get("error_document")
    )
    ensure_enum(
        "services.frontend.config.price_class",
        config.get("price_class"),
        {"PriceClass_100", "PriceClass_200", "PriceClass_All"},
    )


def validate_database(config: dict[str, Any]) -> None:
    reject_unknown_keys(
        "services.database.config", config, ALLOWED_CONFIG_KEYS["database"]
    )
    ensure_enum(
        "services.database.config.billing_mode",
        config.get("billing_mode"),
        {"PAY_PER_REQUEST", "PROVISIONED"},
    )
    ensure_non_empty_string("services.database.config.hash_key", config.get("hash_key"))
    ensure_enum(
        "services.database.config.hash_key_type",
        config.get("hash_key_type"),
        {"S", "N"},
    )

    range_key = ensure_optional_string(
        "services.database.config.range_key", config.get("range_key", "")
    )
    range_key_type = ensure_optional_string(
        "services.database.config.range_key_type", config.get("range_key_type", "")
    )
    if range_key:
        ensure_enum(
            "services.database.config.range_key_type",
            range_key_type,
            {"S", "N"},
        )
    elif range_key_type:
        fail(
            "services.database.config.range_key_type must be empty when range_key is empty"
        )

    if "enable_point_in_time_recovery" in config:
        ensure_bool(
            "services.database.config.enable_point_in_time_recovery",
            config["enable_point_in_time_recovery"],
        )


def validate_storage(config: dict[str, Any]) -> None:
    reject_unknown_keys(
        "services.storage.config", config, ALLOWED_CONFIG_KEYS["storage"]
    )
    ensure_enum(
        "services.storage.config.encryption",
        config.get("encryption"),
        {"AES256", "aws:kms"},
    )
    if "versioning" in config:
        ensure_bool("services.storage.config.versioning", config["versioning"])


def validate_compute(config: dict[str, Any]) -> None:
    reject_unknown_keys(
        "services.compute.config", config, ALLOWED_CONFIG_KEYS["compute"]
    )
    ensure_enum(
        "services.compute.config.runtime",
        config.get("runtime"),
        {"nodejs20.x", "nodejs22.x", "python3.12", "python3.13"},
    )
    ensure_int_range(
        "services.compute.config.memory_size", config.get("memory_size"), 128, 1024
    )
    ensure_int_range("services.compute.config.timeout", config.get("timeout"), 1, 300)

    if "create_function_url" in config:
        ensure_bool(
            "services.compute.config.create_function_url",
            config["create_function_url"],
        )


VALIDATORS = {
    "frontend": validate_frontend,
    "database": validate_database,
    "storage": validate_storage,
    "compute": validate_compute,
}


def validate_service(name: str, service: Any) -> None:
    service_mapping = ensure_mapping(f"services.{name}", service)
    reject_unknown_keys(f"services.{name}", service_mapping, ALLOWED_SERVICE_KEYS)
    expected_type = SERVICE_TYPES[name]
    actual_type = service_mapping.get("type")
    if actual_type != expected_type:
        fail(f"services.{name}.type must equal {expected_type}")

    config = ensure_mapping(f"services.{name}.config", service_mapping.get("config"))
    VALIDATORS[name](config)


def validate_config(config: Any) -> None:
    root = ensure_mapping("config", config)

    for required_key in ("version", "project", "services"):
        if required_key not in root:
            fail(f"missing top-level key: {required_key}")

    if root["version"] != "1":
        fail('version must equal "1"')

    project = ensure_mapping("project", root["project"])
    project_name = ensure_non_empty_string("project.name", project.get("name"))
    if not PROJECT_NAME_RE.fullmatch(project_name):
        fail("project.name must match ^[a-z][a-z0-9-]{2,39}$")

    region = ensure_non_empty_string("project.region", project.get("region"))
    ensure_enum("project.region", region, ALLOWED_REGIONS)
    validate_tags(project.get("tags"))

    services = ensure_mapping("services", root["services"])
    if not services:
        fail("services must contain at least one selected service")

    unknown_services = sorted(set(services) - set(SERVICE_TYPES))
    if unknown_services:
        fail(f"unsupported services present: {', '.join(unknown_services)}")

    for service_name in ("frontend", "database", "storage", "compute"):
        if service_name in services:
            validate_service(service_name, services[service_name])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate an infra.yaml file.")
    parser.add_argument("config_path", help="Path to infra.yaml")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config_path)

    if not config_path.exists():
        fail(f"file not found: {config_path}")

    try:
        with config_path.open("r", encoding="utf-8") as handle:
            config = yaml.safe_load(handle)
    except yaml.YAMLError as exc:
        fail(f"failed to parse YAML: {exc}")

    validate_config(config)
    print("Config valid")


if __name__ == "__main__":
    main()
