#!/usr/bin/env python3
"""
Unit tests for the charger uptime calculator.
"""

import unittest
import tempfile
import os
import sys
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr

# Import the functions from our solution
from charger_uptime import (
    parse_input_file, 
    get_station_reporting_period,
    merge_intervals,
    calculate_station_uptime,
    main
)


class TestChargerUptime(unittest.TestCase):
    
    def create_temp_file(self, content):
        """Helper to create temporary test files."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        temp_file.write(content)
        temp_file.close()
        return temp_file.name
    
    def test_parse_valid_input(self):
        """Test parsing of valid input file."""
        content = """[Stations]
0 1001 1002
1 1003

[Charger Availability Reports]
1001 0 100 true
1002 50 150 false
1003 25 75 true"""
        
        temp_file = self.create_temp_file(content)
        try:
            stations, reports = parse_input_file(temp_file)
            
            expected_stations = {0: [1001, 1002], 1: [1003]}
            expected_reports = [
                (1001, 0, 100, True),
                (1002, 50, 150, False),
                (1003, 25, 75, True)
            ]
            
            self.assertEqual(stations, expected_stations)
            self.assertEqual(reports, expected_reports)
        finally:
            os.unlink(temp_file)
    
    def test_parse_invalid_input_missing_sections(self):
        """Test error handling for missing sections."""
        content = """[Stations]
0 1001"""
        
        temp_file = self.create_temp_file(content)
        try:
            with self.assertRaises(SystemExit):
                with redirect_stdout(StringIO()) as stdout:
                    parse_input_file(temp_file)
        finally:
            os.unlink(temp_file)
    
    def test_merge_intervals(self):
        """Test interval merging logic."""
        # Test overlapping intervals
        intervals = [(0, 50), (25, 75), (100, 150)]
        merged = merge_intervals(intervals)
        expected = [(0, 75), (100, 150)]
        self.assertEqual(merged, expected)
        
        # Test adjacent intervals
        intervals = [(0, 50), (50, 100)]
        merged = merge_intervals(intervals)
        expected = [(0, 100)]
        self.assertEqual(merged, expected)
        
        # Test non-overlapping intervals
        intervals = [(0, 25), (50, 75), (100, 125)]
        merged = merge_intervals(intervals)
        expected = [(0, 25), (50, 75), (100, 125)]
        self.assertEqual(merged, expected)
        
        # Test empty list
        intervals = []
        merged = merge_intervals(intervals)
        expected = []
        self.assertEqual(merged, expected)
    
    def test_get_station_reporting_period(self):
        """Test calculation of station reporting periods."""
        reports = [
            (1001, 0, 100, True),
            (1001, 200, 300, False),
            (1002, 50, 150, True),
            (1003, 25, 75, True)
        ]
        
        # Station with chargers 1001, 1002
        period = get_station_reporting_period([1001, 1002], reports)
        self.assertEqual(period, (0, 300))  # min=0, max=300
        
        # Station with charger 1003 only
        period = get_station_reporting_period([1003], reports)
        self.assertEqual(period, (25, 75))
        
        # Station with no reports
        period = get_station_reporting_period([9999], reports)
        self.assertEqual(period, (0, 0))
    
    def test_calculate_station_uptime_basic(self):
        """Test basic uptime calculations."""
        reports = [
            (1001, 0, 50, True),   # Up for 50 units
            (1001, 50, 100, True), # Up for 50 units
            (1002, 50, 100, True)  # Up for 50 units (overlaps with 1001)
        ]
        
        # Station 0 has chargers 1001, 1002
        # Total period: 0-100 (100 units)
        # Station is up entire time (at least one charger up)
        uptime = calculate_station_uptime(0, [1001, 1002], reports)
        self.assertEqual(uptime, 100)
    
    def test_calculate_station_uptime_with_gaps(self):
        """Test uptime calculation with gaps (downtime)."""
        reports = [
            (1004, 0, 50, True),    # Up 0-50
            (1004, 100, 200, True)  # Up 100-200, gap 50-100 is downtime
        ]
        
        # Station 2 has charger 1004
        # Total period: 0-200 (200 units)
        # Uptime: 50 + 100 = 150 units
        # Percentage: 150/200 * 100 = 75%
        uptime = calculate_station_uptime(2, [1004], reports)
        self.assertEqual(uptime, 75)
    
    def test_calculate_station_uptime_all_down(self):
        """Test uptime calculation when all chargers are down."""
        reports = [
            (1003, 25, 75, False)  # Down entire reporting period
        ]
        
        # Station 1 has charger 1003
        # Total period: 25-75 (50 units)
        # Uptime: 0 units
        # Percentage: 0%
        uptime = calculate_station_uptime(1, [1003], reports)
        self.assertEqual(uptime, 0)
    
    def test_calculate_station_uptime_no_reports(self):
        """Test uptime calculation when charger has no reports."""
        reports = []
        
        # Station with no reports should have 0% uptime
        uptime = calculate_station_uptime(0, [1001], reports)
        self.assertEqual(uptime, 0)
    
    def test_rounding_down(self):
        """Test that uptime percentages are rounded down."""
        
        # Create a scenario where we get 33.33% uptime
        reports = [
            (1001, 0, 10, True),   # Up for 10 units
            (1001, 20, 30, False)  # Down for 10 units, total period 0-30
        ]
        
        # Total period: 0-30 (30 units)
        # Uptime: 10 units
        # Percentage: 10/30 * 100 = 33.33%, should round down to 33
        uptime = calculate_station_uptime(0, [1001], reports)
        self.assertEqual(uptime, 33)


class TestMainFunction(unittest.TestCase):
    
    def create_temp_file(self, content):
        """Helper to create temporary test files."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        temp_file.write(content)
        temp_file.close()
        return temp_file.name
    
    def test_main_with_valid_input(self):
        """Test main function with valid input."""
        content = """[Stations]
0 1001 1002
1 1003

[Charger Availability Reports]
1001 0 100 true
1002 50 150 false
1003 25 75 true"""
        
        temp_file = self.create_temp_file(content)
        try:
            # Capture stdout
            old_argv = sys.argv
            sys.argv = ['charger_uptime.py', temp_file]
            
            with redirect_stdout(StringIO()) as stdout:
                try:
                    main()
                except SystemExit:
                    pass  # main() calls sys.exit(0) on success
            
            output = stdout.getvalue().strip()
            lines = output.split('\n')
            
            # Should have output for stations 0 and 1
            self.assertEqual(len(lines), 2)
            self.assertTrue(lines[0].startswith('0 '))
            self.assertTrue(lines[1].startswith('1 '))
            
        finally:
            sys.argv = old_argv
            os.unlink(temp_file)
    
    def test_main_with_invalid_file(self):
        """Test main function with non-existent file."""
        old_argv = sys.argv
        sys.argv = ['charger_uptime.py', 'nonexistent_file.txt']
        
        try:
            with redirect_stdout(StringIO()) as stdout:
                with self.assertRaises(SystemExit):
                    main()
            
            output = stdout.getvalue().strip()
            self.assertEqual(output, 'ERROR')
        finally:
            sys.argv = old_argv
    
    def test_main_with_wrong_args(self):
        """Test main function with wrong number of arguments."""
        old_argv = sys.argv
        sys.argv = ['charger_uptime.py']  # Missing file argument
        
        try:
            with redirect_stdout(StringIO()) as stdout:
                with self.assertRaises(SystemExit):
                    main()
            
            output = stdout.getvalue().strip()
            self.assertEqual(output, 'ERROR')
        finally:
            sys.argv = old_argv


if __name__ == '__main__':
    unittest.main()
