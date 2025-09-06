# Electric Era Coding Challenge - Charger Uptime Calculator

## Solution Overview

This solution calculates station uptime for electric vehicle charging networks based on individual charger availability reports. The program implements an efficient algorithm to determine the percentage of time that ANY charger at a station was available during the station's reporting period.

## Algorithm Description

### Core Concept
**Station Uptime** = (Time when at least one charger was available) / (Total station reporting period) × 100

### Key Components

1. **Input Parsing**: Robust parsing of the input file format with comprehensive error handling
2. **Station Period Calculation**: Determines the overall reporting period for each station (min start time to max end time across all chargers)
3. **Interval Merging**: Efficiently merges overlapping "up" intervals to calculate total uptime
4. **Percentage Calculation**: Computes uptime percentage and rounds down to nearest integer

### Algorithm Steps

1. Parse input file to extract station-to-charger mappings and availability reports
2. For each station:
   - Calculate the station's overall reporting period (earliest start to latest end time)
   - Collect all "up" intervals for chargers at that station
   - Merge overlapping intervals to get total uptime periods
   - Calculate uptime percentage: (total uptime / total period) × 100
   - Round down to nearest integer
3. Output results sorted by station ID

### Time Complexity
- **O(n log n)** where n is the number of availability reports
- Dominated by sorting operations for interval merging

### Space Complexity
- **O(n)** for storing reports and intermediate data structures

## Implementation Details

### Data Structures
- `stations`: Dictionary mapping station_id → list of charger_ids
- `reports`: List of tuples (charger_id, start_time, end_time, is_up)
- Interval merging uses sorted lists for efficiency

### Edge Cases Handled
1. **Invalid Input Format**: Prints "ERROR" and exits gracefully
2. **Missing Sections**: Validates presence of both [Stations] and [Charger Availability Reports]
3. **Unsigned Integer Validation**: Rejects negative values for station IDs, charger IDs, and timestamps (as per problem constraints)
4. **Station ID Zero**: Properly handles station ID 0 as valid unsigned integer
5. **No Reports for Charger**: Counts as 100% downtime for that charger
6. **Gaps in Reports**: Time gaps between reports count as downtime
7. **Overlapping Intervals**: Properly merges overlapping "up" periods
8. **Rounding**: Always rounds down to nearest integer percentage
9. **File Not Found**: Handles missing input files gracefully

### Ambiguity Resolutions

1. **Station Reporting Period**: Defined as the span from the earliest start time to the latest end time across ALL chargers at that station
2. **Gaps in Reports**: Any time period not covered by an availability report is considered downtime
3. **Overlapping Reports**: Multiple overlapping "up" periods are merged to avoid double-counting
4. **Rounding**: Percentages are rounded DOWN using integer division (as specified in requirements)

## Files Included

- `charger_uptime.py`: Main solution implementation
- `test_solution.py`: Comprehensive unit tests
- `README_solution.md`: This documentation file

## Usage Instructions

### Requirements
- Python 3.6 or higher
- No external dependencies required

### Running the Solution
```bash
python charger_uptime.py <input_file_path>
```

### Example
```bash
python charger_uptime.py input_1.txt
```

### Expected Output Format
```
<Station ID 1> <Uptime Percentage>
<Station ID 2> <Uptime Percentage>
...
```

Station IDs are output in ascending order, with uptime percentages as integers from 0-100.

### Error Handling
If the input is invalid or the file cannot be read, the program outputs:
```
ERROR
```

## Testing

### Running Unit Tests
```bash
python test_solution.py
```

### Running with Verbose Output
```bash
python test_solution.py -v
```

### Test Coverage
The test suite includes:
- Input parsing validation (including unsigned integer constraints)
- Interval merging logic
- Station reporting period calculation
- Uptime calculation with various scenarios
- Error handling for invalid inputs (negative values, missing sections, etc.)
- Edge case testing (station ID zero, negative values)
- Main function integration tests

### Validation Against Provided Examples
The solution has been validated against both provided test cases:

**Test Case 1 (input_1.txt)**:
- Expected: `0 100`, `1 0`, `2 75`
- Actual: `0 100`, `1 0`, `2 75`

**Test Case 2 (input_2.txt)**:
- Expected: `0 66`, `1 100`
- Actual: `0 66`, `1 100`

**Test Suite**: 16 comprehensive unit tests covering all functionality and edge cases

## Design Decisions

### Language Choice
Python was chosen for:
- Clear, readable code that's easy to maintain
- Excellent built-in data structures (dictionaries, lists)
- Strong error handling capabilities
- No compilation required for Linux deployment

### Error Handling Strategy
- Fail fast with "ERROR" output for any invalid input
- Comprehensive validation at each parsing step
- Graceful handling of file I/O errors

### Performance Considerations
- Efficient interval merging algorithm
- Minimal memory usage with appropriate data structures
- O(n log n) time complexity suitable for large datasets

### Maintainability
- Clear function separation with single responsibilities
- Comprehensive documentation and type hints
- Extensive test coverage for confidence in modifications

## Scalability

The solution is designed to handle large datasets efficiently:
- Linear memory usage relative to input size
- Efficient sorting-based algorithms
- No recursive operations that could cause stack overflow
- Suitable for processing thousands of stations and reports

## Compilation and Deployment

### For Linux amd64 Environment
No compilation required. The solution runs directly with Python 3:

```bash
# Make executable (optional)
chmod +x charger_uptime.py

# Run directly
python charger_uptime.py input_file.txt

# Or if made executable with shebang
./charger_uptime.py input_file.txt
```

### Dependencies
- Standard Python 3 library only
- No external packages required
- Compatible with Python 3.6+

## Author Notes

This solution prioritizes correctness, maintainability, and performance. The algorithm handles all specified edge cases and has been thoroughly tested. The code is structured to be easily understood and modified if requirements change.
