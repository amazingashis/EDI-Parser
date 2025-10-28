# EDI 837 (5010) Parser

A comprehensive EDI 837 Health Care Claim parser with web interface that supports X222, X223, and X224 versions. This application parses EDI 837 files and displays the data in human-readable table format.

## Features

- **Complete EDI 837 (5010) Support**: Parses all major segments including ISA, GS, ST, BHT, NM1, CLM, etc.
- **Version Compatibility**: Supports X222, X223, and X224 versions
- **Human-Readable Output**: Displays parsed data in organized table format
- **Web Interface**: Easy-to-use web application for file upload and parsing
- **Multiple Input Methods**: File upload or direct text input
- **Detailed Parsing**: Extracts provider, subscriber, patient, and claim information
- **Error Handling**: Comprehensive error reporting and validation

## Installation

1. Clone or download this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Web Application

1. Start the Flask server:
```bash
python app.py
```

2. Open your browser and go to `http://localhost:5000`

3. Upload an EDI 837 file or paste EDI content directly

4. View parsed results in organized tables:
   - **Summary**: Key fields in human-readable format
   - **Segments**: All EDI segments with descriptions
   - **Raw Data**: Complete parsed data structure

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