#!/usr/bin/env python3
"""
Electric Era Coding Challenge - Charger Uptime Calculator

This program calculates station uptime based on individual charger availability reports.
Station uptime is defined as the percentage of time that ANY charger at a station was
available, out of the entire time period that any charger at that station was reporting.
"""

import sys
from typing import Dict, List, Tuple, Set


def parse_input_file(filepath: str) -> Tuple[Dict[int, List[int]], List[Tuple[int, int, int, bool]]]:
    """
    Parse the input file and extract station mappings and charger availability reports.
    
    Returns:
        stations: Dict mapping station_id -> list of charger_ids
        reports: List of (charger_id, start_time, end_time, is_up) tuples
    """
    try:
        with open(filepath, 'r') as f:
            content = f.read().strip()
    except (FileNotFoundError, IOError):
        print("ERROR")
        sys.exit(1)
    
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    
    if len(lines) < 2:
        print("ERROR")
        sys.exit(1)
    
    # Find section boundaries
    stations_start = -1
    reports_start = -1
    
    for i, line in enumerate(lines):
        if line == "[Stations]":
            stations_start = i + 1
        elif line == "[Charger Availability Reports]":
            reports_start = i + 1
            break
    
    if stations_start == -1 or reports_start == -1:
        print("ERROR")
        sys.exit(1)
    
    # Parse stations section
    stations = {}
    try:
        for i in range(stations_start, reports_start - 1):
            parts = lines[i].split()
            if len(parts) < 2:
                print("ERROR")
                sys.exit(1)
            
            station_id = int(parts[0])
            charger_ids = [int(x) for x in parts[1:]]
            stations[station_id] = charger_ids
    except (ValueError, IndexError):
        print("ERROR")
        sys.exit(1)
    
    # Parse availability reports section
    reports = []
    try:
        for i in range(reports_start, len(lines)):
            parts = lines[i].split()
            if len(parts) != 4:
                print("ERROR")
                sys.exit(1)
            
            charger_id = int(parts[0])
            start_time = int(parts[1])
            end_time = int(parts[2])
            is_up = parts[3].lower() == 'true'
            
            if start_time >= end_time:
                print("ERROR")
                sys.exit(1)
            
            reports.append((charger_id, start_time, end_time, is_up))
    except (ValueError, IndexError):
        print("ERROR")
        sys.exit(1)
    
    return stations, reports


def get_station_reporting_period(station_id: int, charger_ids: List[int], 
                               reports: List[Tuple[int, int, int, bool]]) -> Tuple[int, int]:
    """
    Calculate the overall reporting period for a station based on all its chargers.
    
    Returns:
        (min_start_time, max_end_time) for the station
    """
    station_chargers = set(charger_ids)
    min_start = None
    max_end = None
    
    for charger_id, start_time, end_time, _ in reports:
        if charger_id in station_chargers:
            if min_start is None or start_time < min_start:
                min_start = start_time
            if max_end is None or end_time > max_end:
                max_end = end_time
    
    if min_start is None or max_end is None:
        return 0, 0
    
    return min_start, max_end


def merge_intervals(intervals: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """
    Merge overlapping intervals and return a sorted list of non-overlapping intervals.
    """
    if not intervals:
        return []
    
    # Sort intervals by start time
    intervals.sort()
    merged = [intervals[0]]
    
    for current_start, current_end in intervals[1:]:
        last_start, last_end = merged[-1]
        
        if current_start <= last_end:
            # Overlapping intervals, merge them
            merged[-1] = (last_start, max(last_end, current_end))
        else:
            # Non-overlapping interval
            merged.append((current_start, current_end))
    
    return merged


def calculate_station_uptime(station_id: int, charger_ids: List[int], 
                           reports: List[Tuple[int, int, int, bool]]) -> int:
    """
    Calculate the uptime percentage for a station.
    
    Returns:
        Uptime percentage (0-100), rounded down to nearest integer
    """
    # Get the overall reporting period for this station
    period_start, period_end = get_station_reporting_period(station_id, charger_ids, reports)
    
    if period_start == period_end:
        return 0
    
    total_period = period_end - period_start
    station_chargers = set(charger_ids)
    
    # Collect all "up" intervals for chargers at this station
    up_intervals = []
    for charger_id, start_time, end_time, is_up in reports:
        if charger_id in station_chargers and is_up:
            up_intervals.append((start_time, end_time))
    
    # Merge overlapping up intervals
    merged_up_intervals = merge_intervals(up_intervals)
    
    # Calculate total uptime within the station's reporting period
    total_uptime = 0
    for start, end in merged_up_intervals:
        # Clip interval to station's reporting period
        clipped_start = max(start, period_start)
        clipped_end = min(end, period_end)
        
        if clipped_start < clipped_end:
            total_uptime += clipped_end - clipped_start
    
    # Calculate percentage and round down
    uptime_percentage = (total_uptime * 100) // total_period
    return int(uptime_percentage)


def main():
    if len(sys.argv) != 2:
        print("ERROR")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    # Parse input file
    stations, reports = parse_input_file(input_file)
    
    # Validate that all chargers in reports belong to some station
    all_station_chargers = set()
    for charger_ids in stations.values():
        all_station_chargers.update(charger_ids)
    
    report_chargers = set(charger_id for charger_id, _, _, _ in reports)
    
    # It's okay if some chargers have no reports (they count as 100% downtime)
    # But all chargers in reports should belong to some station
    for charger_id in report_chargers:
        if charger_id not in all_station_chargers:
            print("ERROR")
            sys.exit(1)
    
    # Calculate uptime for each station
    results = []
    for station_id, charger_ids in stations.items():
        uptime = calculate_station_uptime(station_id, charger_ids, reports)
        results.append((station_id, uptime))
    
    # Sort by station ID and output
    results.sort()
    for station_id, uptime in results:
        print(f"{station_id} {uptime}")


if __name__ == "__main__":
    main()
