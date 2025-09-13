#!/usr/bin/env python3
"""
Live Simulation Runner

This module provides a standalone runner for live simulation (paper trading)
that can be executed independently or by the persistent bot script.
"""

import sys
import asyncio
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.cli.simulate import simulate_cli

def main():
    """Main entry point for live simulation."""
    try:
        # Set up sys.argv for the simulation CLI
        sys.argv = ['simulate', '--profile', 'live_eth']
        
        # Run the simulation
        simulate_cli()
        
    except KeyboardInterrupt:
        print("\nLive simulation interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Live simulation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
