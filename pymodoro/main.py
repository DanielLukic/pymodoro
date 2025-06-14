#!/usr/bin/env python3

import sys
import argparse
from PyQt6.QtWidgets import QApplication
from .app import PyomodoroApp
from .config.provider import ConfigProvider, PersistentConfig, InMemoryConfig
from .utils.logger import setup_logger, parse_log_level

def parse_duration(duration_str):
    """Parse duration string like '15s', '2m', '1h' into seconds"""
    if duration_str.endswith('s'):
        return int(duration_str[:-1])
    elif duration_str.endswith('m'):
        return int(duration_str[:-1]) * 60
    elif duration_str.endswith('h'):
        return int(duration_str[:-1]) * 3600
    else:
        return int(duration_str)

def parse_args():
    parser = argparse.ArgumentParser(
        description='Pymodoro - Linux Pomodoro Timer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py                    # Normal mode (25m work, 5m break)
  python run.py 15s 5s 4 10s       # Test mode (15s work, 5s break, 4 cycles, 10s long break)
  python run.py 2m 30s 2 1m        # Quick test (2m work, 30s break, 2 cycles, 1m long break)
  
Logging:
  python run.py --log-level DEBUG  # Enable debug logging
  python run.py --log-file /tmp/pymodoro.log  # Custom log file
        """
    )
    
    # Timer arguments
    parser.add_argument('work_duration', nargs='?', 
                       help='Work duration (e.g., 25m, 15s, 2h)')
    parser.add_argument('short_break_duration', nargs='?',
                       help='Short break duration (e.g., 5m, 10s)')
    parser.add_argument('sessions_until_long_break', nargs='?', type=int,
                       help='Sessions before long break (e.g., 4)')
    parser.add_argument('long_break_duration', nargs='?',
                       help='Long break duration (e.g., 15m, 10s)')
    
    # Logging arguments
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       default='INFO', help='Set logging level (default: INFO)')
    parser.add_argument('--log-file', help='Custom log file path')
    parser.add_argument('--no-clear-log', action='store_true', 
                       help='Don\'t clear log file at startup')
    
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Initialize logging first
    log_level = parse_log_level(args.log_level)
    logger = setup_logger(
        level=log_level,
        log_file=args.log_file,
        clear_log=not args.no_clear_log
    )
    
    logger.info("Starting Pymodoro application")
    
    # Initialize ConfigProvider based on command line arguments
    if args.work_duration:
        # Test mode - use InMemoryConfig
        test_config = {}
        
        work_seconds = parse_duration(args.work_duration)
        test_config['_work_seconds'] = work_seconds
        
        if args.short_break_duration:
            test_config['_short_break_seconds'] = parse_duration(args.short_break_duration)
        
        if args.sessions_until_long_break:
            test_config['sessions_until_long_break'] = args.sessions_until_long_break
            
        if args.long_break_duration:
            test_config['_long_break_seconds'] = parse_duration(args.long_break_duration)
        
        logger.info("🧪 TEST MODE ACTIVE")
        logger.info(f"Work: {test_config['_work_seconds']}s")
        if '_short_break_seconds' in test_config:
            logger.info(f"Short break: {test_config['_short_break_seconds']}s")
        if 'sessions_until_long_break' in test_config:
            logger.info(f"Sessions until long break: {test_config['sessions_until_long_break']}")
        if '_long_break_seconds' in test_config:
            logger.info(f"Long break: {test_config['_long_break_seconds']}s")
        
        # Initialize with InMemoryConfig
        ConfigProvider.initialize(InMemoryConfig(test_config))
    else:
        # Normal mode - use PersistentConfig
        logger.info("Normal mode - using persistent configuration")
        ConfigProvider.initialize(PersistentConfig())
    
    # Create and run the application
    try:
        pomodoro_app = PyomodoroApp()
        exit_code = pomodoro_app.run()
        logger.info(f"Application exited with code: {exit_code}")
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main() 