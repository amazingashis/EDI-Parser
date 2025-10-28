# EDI 837 (5010) Parser

A comprehensive EDI 837 Health Care Claim parser with web interface that supports X222, X223, and X224 versions. This application parses EDI 837 files and displays the data in human-readable table format.

## Features

- ✅ **Full EDI 837 (5010) Support**: Parses professional health care claims
- ✅ **Version Compatibility**: X222/X223/X224 support
- ✅ **Advanced Web Interface**: Multiple view modes and visualization options
- ✅ **Element-Level Parsing**: Detailed breakdown of each EDI element with positions and descriptions
- ✅ **Multiple View Modes**: 
  - **Summary View**: Key information in human-readable tables
  - **Element Details**: Grouped segments with toggle to flattened spreadsheet view
  - **Tree View**: Hierarchical structure with expandable nodes
  - **Statistics**: Interactive charts and coverage metrics
  - **Raw Data**: Complete JSON structure
- ✅ **Advanced Search & Filtering**: Real-time search across all elements with segment and presence filters
- ✅ **Visual Enhancements**: Color-coded segments, progress bars, and interactive charts
- ✅ **Export Features**: Copy to clipboard or export flattened data as CSV
- ✅ **Comprehensive Parsing**: Extracts all major segments and fields
- ✅ **Error Handling**: Robust error detection and reporting

## Installation

1. Clone or download this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### 3. Access the Enhanced Interface
Open your browser and go to: http://localhost:5000

### 4. Explore the Visualization Features
- **Summary Tab**: Overview of key EDI fields
- **Element Details Tab**: 
  - Toggle between grouped view (cards) and flattened view (table)
  - Search and filter elements in real-time
  - Copy data to clipboard or export as CSV
- **Tree View Tab**: Navigate EDI structure hierarchically
- **Statistics Tab**: View parsing coverage and segment distribution charts

### Using the Parser Directly

```python
from edi_parser import EDI837Parser

# Create parser instance
parser = EDI837Parser()

# Parse EDI content
with open('sample_837.txt', 'r') as f:
    content = f.read()

result = parser.parse_file(content)

if result['success']:
    # Get human-readable summary
    summary = parser.get_summary_table()
    for item in summary:
        print(f"{item['Section']} - {item['Field']}: {item['Value']}")
else:
    print(f"Error: {result['error']}")
```

## Supported EDI Segments

- **ISA**: Interchange Control Header
- **GS**: Functional Group Header  
- **ST**: Transaction Set Header
- **BHT**: Beginning of Hierarchical Transaction
- **NM1**: Individual or Organizational Name
- **N3**: Party Location
- **N4**: Geographic Location
- **REF**: Reference Information
- **PER**: Administrative Communications Contact
- **HL**: Hierarchical Level
- **PRV**: Provider Information
- **SBR**: Subscriber Information
- **PAT**: Patient Information
- **CLM**: Claim Information
- **DTP**: Date or Time or Period
- **HI**: Health Care Diagnosis Code
- **SV1**: Professional Service
- **SE**: Transaction Set Trailer
- **GE**: Functional Group Trailer
- **IEA**: Interchange Control Trailer

## Entity Types Supported

- **40**: Receiver
- **41**: Submitter
- **85**: Billing Provider
- **87**: Pay-to Provider
- **IL**: Insured or Subscriber
- **QC**: Patient
- **PR**: Payer
- **DN**: Referring Provider
- **P3**: Primary Care Provider
- **82**: Rendering Provider

## File Formats

Supports the following file extensions:
- `.txt`
- `.edi`
- `.x12`
- `.837`

## Sample EDI Content

The application includes a sample EDI 837 file for testing. Click "Load Sample" in the web interface to see it in action.

## API Endpoints

- `GET /`: Main web interface
- `POST /upload`: Upload and parse EDI file
- `POST /parse_text`: Parse EDI content from text
- `GET /sample`: Load sample EDI data

## Error Handling

The parser includes comprehensive error handling for:
- Invalid file formats
- Malformed EDI segments
- Missing required fields
- Encoding issues

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.