#!/usr/bin/env python3
"""
Test script for EDI 837 Parser
Demonstrates parsing functionality with sample data
"""

from edi_parser import EDI837Parser

def test_sample_edi():
    """Test the parser with sample EDI 837 data"""
    
    # Sample EDI 837 (5010) data
    sample_edi = """ISA*00*          *00*          *ZZ*SUBMITTER      *ZZ*RECEIVER       *101127*1719*^*00501*000000905*0*P*:~GS*HC*SUBMITTER*RECEIVER*20101127*1719*1*X*005010X222A1~ST*837*0001*005010X222A1~BHT*0019*00*244579*20061015*1023*CH~NM1*41*2*PREMIER BILLING SERVICE*****46*TGJ23~PER*IC*CONTACT NAME*TE*7176149999~NM1*40*2*KEY INSURANCE COMPANY*****46*66783JJT~HL*1**20*1~PRV*BI*PXC*203BF0100Y~NM1*85*2*BEN KILDARE SERVICE*****XX*9876543210~N3*234 SEAWAY ST~N4*MIAMI*FL*33111~REF*EI*587654321~HL*2*1*22*0~SBR*P*18*******CI~NM1*IL*1*SMITH*JANE****MI*JS00111223333~N3*236 N MAIN ST~N4*MIAMI*FL*33413~DMG*D8*19430501*F~NM1*PR*2*KEY INSURANCE COMPANY*****PI*999996666~CLM*26463774*100***11:B:1*Y*A*Y*I~DTP*431*D8*20061003~REF*D9*17312345600006351~HI*BK:0340*BF:V7389~LX*1~SV1*HC:99213*40*UN*1***1~DTP*472*D8*20061003~SE*23*0001~GE*1*1~IEA*1*000000905~"""
    
    print("EDI 837 (5010) Parser Test")
    print("=" * 50)
    
    # Create parser instance
    parser = EDI837Parser()
    
    # Parse the sample data
    result = parser.parse_file(sample_edi)
    
    if result['success']:
        print("✅ Parsing successful!")
        print(f"Found {len(result['segments'])} segments")
        
        # Display summary table
        print("\n📋 HUMAN-READABLE SUMMARY:")
        print("-" * 80)
        summary = parser.get_summary_table()
        
        current_section = None
        for item in summary:
            if item['Section'] != current_section:
                current_section = item['Section']
                print(f"\n🏷️  {current_section}:")
                print("-" * 40)
            
            print(f"  {item['Field']:<25}: {item['Value']:<20} ({item['Description']})")
        
        # Display segment breakdown
        print(f"\n🔧 SEGMENT BREAKDOWN:")
        print("-" * 80)
        for segment in result['segments'][:10]:  # Show first 10 segments
            print(f"  {segment['tag']:<5}: {segment['description']}")
            if segment['elements']:
                print(f"        Elements: {' | '.join(segment['elements'][:5])}")  # Show first 5 elements
        
        if len(result['segments']) > 10:
            print(f"        ... and {len(result['segments']) - 10} more segments")
        
        # Display parsed data overview
        print(f"\n📊 PARSED DATA OVERVIEW:")
        print("-" * 80)
        data = result['data']
        print(f"  Providers found: {len(data.get('providers', []))}")
        print(f"  Subscribers found: {len(data.get('subscribers', []))}")
        print(f"  Patients found: {len(data.get('patients', []))}")
        print(f"  Claims found: {len(data.get('claims', []))}")
        
        # Show version compatibility
        ic = data.get('interchange_control', {})
        version = ic.get('version', '')
        print(f"\n🔍 VERSION COMPATIBILITY:")
        print("-" * 80)
        print(f"  EDI Version: {version}")
        if version in ['00501']:
            print("  ✅ Compatible with X222/X223/X224")
        else:
            print("  ⚠️  Version compatibility unknown")
        
    else:
        print("❌ Parsing failed!")
        print(f"Error: {result.get('error', 'Unknown error')}")
        if result.get('errors'):
            for error in result['errors']:
                print(f"  - {error}")

def test_parser_methods():
    """Test individual parser methods"""
    print("\n\n🧪 TESTING PARSER METHODS:")
    print("=" * 50)
    
    parser = EDI837Parser()
    
    # Test segment definitions
    print(f"Supported segments: {len(parser.segment_definitions)}")
    print(f"Entity types: {len(parser.entity_types)}")
    
    # Test with empty content
    result = parser.parse_file("")
    print(f"Empty content test: {'✅ Handled gracefully' if not result['success'] else '❌ Should fail'}")
    
    # Test with malformed content
    result = parser.parse_file("INVALID*EDI*CONTENT")
    print(f"Invalid content test: {'✅ Handled gracefully' if not result['success'] else '❌ Should fail'}")

if __name__ == "__main__":
    test_sample_edi()
    test_parser_methods()
    
    print("\n" + "=" * 50)
    print("🚀 Web Application Access:")
    print("   Open your browser and go to: http://localhost:5000")
    print("   - Upload EDI files or paste content directly")
    print("   - View results in organized tables")
    print("   - Compatible with X222/X223/X224 versions")
    print("=" * 50)