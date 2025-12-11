# Universal EDI Parser (837 & 820)

A comprehensive universal EDI parser with web interface that supports both EDI 837 (Healthcare Claims) and EDI 820 (Payment Order/Remittance Advice) transactions. This application parses both EDI 837 and 820 files and displays the data in human-readable table format.

## Features

- ✅ **Full EDI 837 (5010) Support**: Parses professional health care claims (X222/X223/X224 versions)
- ✅ **Full EDI 820 (5010) Support**: Parses payment orders and remittance advice
- ✅ **Automatic Transaction Detection**: Automatically detects and parses EDI 837 or 820 transactions
- ✅ **Advanced Web Interface**: Multiple view modes and visualization options for both transaction types
- ✅ **Element-Level Parsing**: Detailed breakdown of each EDI element with positions and descriptions
- ✅ **Multiple View Modes**: 
  - **Summary View**: Key information in human-readable tables
  - **Element Details**: Grouped segments with toggle to flattened spreadsheet view
  - **Tree View**: Hierarchical structure with expandable nodes
  - **Statistics**: Interactive charts and coverage metrics (transaction-specific)
  - **Raw Data**: Complete JSON structure
- ✅ **Advanced Search & Filtering**: Real-time search across all elements with segment and presence filters
- ✅ **Visual Enhancements**: Color-coded segments, progress bars, and interactive charts
- ✅ **Export Features**: Copy to clipboard or export flattened data as CSV
- ✅ **Comprehensive Parsing**: Extracts all major segments and fields for both transaction types
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
from edi_parser import UniversalEDIParser

# Create parser instance
parser = UniversalEDIParser()

# Parse EDI content (automatically detects 837 or 820)
with open('sample_837.txt', 'r') as f:  # or sample_820.txt
    content = f.read()

result = parser.parse_file(content)

if result['success']:
    # Check transaction type
    print(f"Transaction Type: EDI {result['transaction_type']}")
    
    # Get human-readable summary
    summary = parser.get_summary_table()
    for item in summary:
        print(f"{item['Section']} - {item['Field']}: {item['Value']}")
        
    # Get detailed analysis
    data_summary = parser.get_data_summary()
    print(f"Transaction Type: {data_summary['transaction_type']}")
    
    # Access transaction-specific data
    if result['transaction_type'] == '837':
        claims = result['data']['claims']
        providers = result['data']['providers']
        print(f"Claims: {len(claims)}, Providers: {len(providers)}")
    elif result['transaction_type'] == '820':
        payment_info = result['data']['payment_info']
        remittances = result['data']['remittance_data']
        print(f"Payment Amount: ${payment_info.get('payment_amount', 'N/A')}")
        print(f"Remittances: {len(remittances)}")
else:
    print(f"Error: {result['error']}")
```

## Supported EDI Transactions

### EDI 837 (Healthcare Claims)
**Segments:**

### EDI 837 (Healthcare Claims)
**Segments:**
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

### EDI 820 (Payment Order/Remittance Advice)
**Segments:**
- **ISA**: Interchange Control Header
- **GS**: Functional Group Header
- **ST**: Transaction Set Header
- **BPR**: Beginning Segment for Payment Order/Remittance Advice
- **TRN**: Trace
- **NM1**: Individual or Organizational Name
- **N3**: Party Location
- **N4**: Geographic Location
- **DTM**: Date/Time Reference
- **RMR**: Remittance Advice
- **SVC**: Service Payment Information
- **CAS**: Claims Adjustment
- **PLB**: Provider Level Adjustment
- **SE**: Transaction Set Trailer
- **GE**: Functional Group Trailer
- **IEA**: Interchange Control Trailer

## Entity Types Supported

### EDI 837 Entity Types
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

### EDI 820 Entity Types
- **PE**: Payee
- **PR**: Payer
- **TT**: Third Party Administrator
- **GP**: Group
- **BO**: Broker or Sales Office
- **FA**: Facility

## File Formats

Supports the following file extensions:
- `.txt`
- `.edi`
- `.x12`
- `.837`
- `.820`

## Sample EDI Content

The application includes sample files for both transaction types:
- **EDI 837**: Click "Load Sample" in the web interface
- **EDI 820**: Available via the `/sample820` endpoint

## API Endpoints

- `GET /`: Main web interface
- `POST /upload`: Upload and parse EDI file (supports both 837 and 820)
- `POST /parse_text`: Parse EDI content from text (auto-detects transaction type)
- `GET /sample`: Load sample EDI 837 data
- `GET /sample820`: Load sample EDI 820 data

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