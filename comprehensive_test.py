"""
Enhanced test script for EDI 837 Parser
Demonstrates parsing real EDI 837 content and displaying results
"""

import sys
import os

# Add the current directory to Python path
sys.path.append('/workspaces/EDI-Parser')

from edi_parser import EDI837Parser

def main():
    print("🧪 COMPREHENSIVE EDI 837 PARSER TEST")
    print("=" * 60)
    
    # Load sample EDI file
    sample_file = '/workspaces/EDI-Parser/sample_edi_837.txt'
    
    try:
        with open(sample_file, 'r') as f:
            edi_content = f.read().strip()
        
        print(f"📄 Loaded sample EDI file: {len(edi_content)} characters")
        print(f"📋 Number of segments: {edi_content.count('~')}")
        print()
        
        # Parse the EDI content
        parser = EDI837Parser()
        result = parser.parse_file(edi_content)
        
        if result['success']:
            print("✅ PARSING SUCCESSFUL!")
            print(f"📊 Parsed Data Keys: {list(result['data'].keys())}")
            print(f"🔧 Total Segments: {len(result['segments'])}")
            print()
            
            # Display segments information
            print("� PARSED SEGMENTS:")
            print("-" * 40)
            segment_counts = {}
            for segment in result['segments']:
                tag = segment['tag']
                segment_counts[tag] = segment_counts.get(tag, 0) + 1
            
            for tag, count in segment_counts.items():
                description = result['segments'][0]['description'] if result['segments'] else 'Unknown'
                for seg in result['segments']:
                    if seg['tag'] == tag:
                        description = seg['description']
                        break
                print(f"  {tag}: {count} occurrence(s) - {description}")
            print()
            
            # Display parsed data structure
            print("� PARSED DATA STRUCTURE:")
            print("-" * 40)
            for key, value in result['data'].items():
                if isinstance(value, list):
                    print(f"  {key}: {len(value)} item(s)")
                elif isinstance(value, dict):
                    print(f"  {key}: {len(value)} key(s)")
                else:
                    print(f"  {key}: {value}")
            print()
            
            # Display claims if available
            if result['data'].get('claims'):
                print("💰 CLAIMS INFORMATION:")
                print("-" * 40)
                for i, claim in enumerate(result['data']['claims'], 1):
                    print(f"  Claim {i}: {claim}")
                print()
            
            # Display providers if available
            if result['data'].get('providers'):
                print("🏥 PROVIDER INFORMATION:")
                print("-" * 40)
                for i, provider in enumerate(result['data']['providers'], 1):
                    print(f"  Provider {i}: {provider}")
                print()
            
            # Display errors if any
            if result['errors']:
                print("⚠️ PARSING WARNINGS/ERRORS:")
                print("-" * 40)
                for error in result['errors']:
                    print(f"  • {error}")
                print()
            
            # Display summary
            print("📈 PARSING SUMMARY:")
            print("-" * 40)
            print(f"  Total Segments Parsed: {len(result['segments'])}")
            print(f"  Recognized Segments: {sum(1 for seg in result['segments'] if seg['description'] != 'Unknown')}")
            print(f"  Claims Found: {len(result['data'].get('claims', []))}")
            print(f"  Providers: {len(result['data'].get('providers', []))}")
            print(f"  Subscribers: {len(result['data'].get('subscribers', []))}")
            print(f"  Patients: {len(result['data'].get('patients', []))}")
            
        else:
            print("❌ PARSING FAILED!")
            print(f"Error: {result['error']}")
    
    except FileNotFoundError:
        print(f"❌ Sample file not found: {sample_file}")
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
    
    print()
    print("🌐 WEB APPLICATION ACCESS:")
    print("-" * 40)
    print("  URL: http://localhost:5000")
    print("  Features:")
    print("    • Upload EDI files")
    print("    • Paste EDI content directly")
    print("    • View parsed data in tables")
    print("    • Export results")
    print("    • Compatible with X222/X223/X224")

if __name__ == "__main__":
    main()