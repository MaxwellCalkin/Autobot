#!/usr/bin/env python3
"""
Autobot Observation Analyzer - Mine patterns from observations.jsonl.

Utility script for querying and analyzing observations logged during
autonomous development sessions.

Usage:
  python analyze-observations.py --type test_failure
  python analyze-observations.py --type pattern
  python analyze-observations.py --recent 10
  python analyze-observations.py --summary
"""
import json
import sys
import argparse
from pathlib import Path
from collections import Counter
from datetime import datetime


def load_observations(path: Path) -> list[dict]:
    """Load all observations from JSONL file."""
    observations = []
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        observations.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    return observations


def filter_by_type(observations: list[dict], obs_type: str) -> list[dict]:
    """Filter observations by type."""
    return [o for o in observations if o.get('type') == obs_type]


def get_recent(observations: list[dict], count: int) -> list[dict]:
    """Get most recent observations."""
    return observations[-count:] if len(observations) > count else observations


def print_summary(observations: list[dict]) -> None:
    """Print summary statistics."""
    if not observations:
        print("No observations found.")
        return

    type_counts = Counter(o.get('type', 'unknown') for o in observations)
    file_counts = Counter(o.get('file', 'unknown') for o in observations if o.get('file'))

    print("=== OBSERVATION SUMMARY ===\n")
    print(f"Total observations: {len(observations)}")

    print("\nBy Type:")
    for obs_type, count in type_counts.most_common():
        print(f"  {obs_type}: {count}")

    print("\nMost Affected Files:")
    for file_path, count in file_counts.most_common(5):
        print(f"  {file_path}: {count}")

    # Time range
    timestamps = [o.get('timestamp') for o in observations if o.get('timestamp')]
    if timestamps:
        print(f"\nTime Range:")
        print(f"  First: {min(timestamps)}")
        print(f"  Last: {max(timestamps)}")


def print_observations(observations: list[dict]) -> None:
    """Print observations in readable format."""
    for i, obs in enumerate(observations, 1):
        print(f"\n--- Observation {i} ---")
        print(f"Type: {obs.get('type', 'unknown')}")
        print(f"Time: {obs.get('timestamp', 'unknown')}")
        if obs.get('file'):
            print(f"File: {obs.get('file')}")
        if obs.get('message'):
            print(f"Message: {obs.get('message')}")
        if obs.get('output_snippet'):
            print(f"Output: {obs.get('output_snippet')[:200]}...")


def main():
    parser = argparse.ArgumentParser(description='Analyze Autobot observations')
    parser.add_argument('--type', help='Filter by observation type')
    parser.add_argument('--recent', type=int, help='Show N most recent observations')
    parser.add_argument('--summary', action='store_true', help='Show summary statistics')
    parser.add_argument('--path', default='.autobot/observations.jsonl',
                        help='Path to observations file')

    args = parser.parse_args()

    obs_path = Path(args.path)
    observations = load_observations(obs_path)

    if args.type:
        observations = filter_by_type(observations, args.type)
        print(f"Filtered to {len(observations)} observations of type '{args.type}'")

    if args.recent:
        observations = get_recent(observations, args.recent)

    if args.summary:
        print_summary(observations)
    else:
        print_observations(observations)


if __name__ == "__main__":
    main()
