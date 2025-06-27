#!/usr/bin/env python3
"""
Test script for tap-hubspot implementation
Tests the actual tap-hubspot code with discovery and sync modes
"""

import json
import os
import sys
import subprocess
import tempfile
from datetime import datetime, timedelta
import pytz

CONFIG_FILE = "config.sample.json"

def load_config():
    """Load config from config.sample.json"""
    if not os.path.exists(CONFIG_FILE):
        print(f"❌ Config file {CONFIG_FILE} not found.")
        return None
    with open(CONFIG_FILE) as f:
        config = json.load(f)
    required = ["client_id", "client_secret", "refresh_token"]
    for key in required:
        if key not in config or not config[key]:
            print(f"❌ Missing required config value: {key}")
            return None
    return config

def run_tap_command(args):
    """Run tap-hubspot command and return output"""
    try:
        result = subprocess.run(
            ['python', 'tap_hubspot/__init__.py'] + args,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)

def test_discovery():
    """Test tap discovery mode"""
    print(f"\n{'='*60}")
    print("🔍 Testing tap-hubspot Discovery Mode")
    print(f"{'='*60}")

    config = load_config()
    if not config:
        return False

    # Create a temporary config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f)
        config_path = f.name

    try:
        returncode, stdout, stderr = run_tap_command(['--config', config_path, '--discover'])

        print(f"Return Code: {returncode}")
        if stdout:
            print(f"✅ STDOUT: {stdout[:1000]}...")  # Show first 1000 chars
        if stderr:
            print(f"⚠️  STDERR: {stderr}")

        if returncode == 0:
            print("✅ Discovery mode completed successfully!")
            return True
        else:
            print("❌ Discovery mode failed!")
            return False

    finally:
        os.unlink(config_path)

def test_sync_with_catalog():
    """Test tap sync mode with a catalog"""
    print(f"\n{'='*60}")
    print("🔄 Testing tap-hubspot Sync Mode")
    print(f"{'='*60}")

    config = load_config()
    if not config:
        return False

    # Create a temporary config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f)
        config_path = f.name

    # Create a simple catalog with just contacts stream
    catalog = {
        "streams": [
            {
                "tap_stream_id": "contacts",
                "stream": "contacts",
                "schema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "updatedAt": {"type": "string", "format": "date-time"},
                        "properties": {"type": "object"}
                    }
                },
                "metadata": [
                    {
                        "breadcrumb": [],
                        "metadata": {
                            "selected": True,
                            "table-key-properties": ["id"],
                            "valid-replication-keys": ["updatedAt"],
                            "forced-replication-method": "INCREMENTAL"
                        }
                    },
                    {
                        "breadcrumb": ["properties", "id"],
                        "metadata": {"inclusion": "automatic"}
                    },
                    {
                        "breadcrumb": ["properties", "updatedAt"],
                        "metadata": {"inclusion": "automatic"}
                    }
                ]
            }
        ]
    }

    # Create a temporary catalog file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(catalog, f)
        catalog_path = f.name

    try:
        returncode, stdout, stderr = run_tap_command([
            '--config', config_path,
            '--properties', catalog_path
        ])

        print(f"Return Code: {returncode}")
        if stdout:
            print(f"✅ STDOUT: {stdout[:1000]}...")  # Show first 1000 chars
        if stderr:
            print(f"⚠️  STDERR: {stderr}")

        if returncode == 0:
            print("✅ Sync mode completed successfully!")
            return True
        else:
            print("❌ Sync mode failed!")
            return False

    finally:
        os.unlink(config_path)
        os.unlink(catalog_path)

def test_events_stream():
    """Test the events stream specifically"""
    print(f"\n{'='*60}")
    print("🎯 Testing Events Stream")
    print(f"{'='*60}")

    config = load_config()
    if not config:
        return False

    # Create a temporary config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f)
        config_path = f.name

    # Create a catalog with events stream
    catalog = {
        "streams": [
            {
                "tap_stream_id": "events",
                "stream": "events",
                "schema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "occurredAt": {"type": "string", "format": "date-time"},
                        "eventType": {"type": "string"},
                        "properties": {"type": "object"}
                    }
                },
                "metadata": [
                    {
                        "breadcrumb": [],
                        "metadata": {
                            "selected": True,
                            "table-key-properties": ["id"],
                            "valid-replication-keys": ["occurredAt"],
                            "forced-replication-method": "INCREMENTAL"
                        }
                    },
                    {
                        "breadcrumb": ["properties", "id"],
                        "metadata": {"inclusion": "automatic"}
                    },
                    {
                        "breadcrumb": ["properties", "occurredAt"],
                        "metadata": {"inclusion": "automatic"}
                    }
                ]
            }
        ]
    }

    # Create a temporary catalog file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(catalog, f)
        catalog_path = f.name

    try:
        returncode, stdout, stderr = run_tap_command([
            '--config', config_path,
            '--properties', catalog_path
        ])

        print(f"Return Code: {returncode}")
        if stdout:
            print(f"✅ STDOUT: {stdout[:1000]}...")  # Show first 1000 chars
        if stderr:
            print(f"⚠️  STDERR: {stderr}")

        if returncode == 0:
            print("✅ Events stream sync completed successfully!")
            return True
        else:
            print("❌ Events stream sync failed!")
            return False

    finally:
        os.unlink(config_path)
        os.unlink(catalog_path)

def main():
    print("🧪 Testing tap-hubspot Implementation")
    print("=" * 50)

    # Test discovery mode
    discovery_success = test_discovery()

    # Test sync mode with contacts
    sync_success = test_sync_with_catalog()

    # Test events stream
    events_success = test_events_stream()

    print(f"\n{'='*60}")
    print("📊 Test Results Summary")
    print(f"{'='*60}")
    print(f"Discovery Mode: {'✅ PASSED' if discovery_success else '❌ FAILED'}")
    print(f"Sync Mode (Contacts): {'✅ PASSED' if sync_success else '❌ FAILED'}")
    print(f"Events Stream: {'✅ PASSED' if events_success else '❌ FAILED'}")

    if all([discovery_success, sync_success, events_success]):
        print("\n🎉 All tests passed! tap-hubspot is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()