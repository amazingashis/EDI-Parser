"""
Enhanced test for element-level EDI 837 parsing
Demonstrates the new detailed element parsing capabilities
"""

import sys
import os

# Add the current directory to Python path
sys.path.append('/workspaces/EDI-Parser')

from edi_parser import EDI837Parser

def main():
    print("🔬 ELEMENT-LEVEL EDI 837 PARSER TEST")
    print("=" * 60)
    
    # Load sample EDI file
    sample_file = '/workspaces/EDI-Parser/sample_edi_837.txt'
    
    try:
        with open(sample_file, 'r') as f:
            edi_content = f.read().strip()
        
        print(f"📄 Loaded sample EDI file: {len(edi_content)} characters")
        print()
        
        # Parse the EDI content
        parser = EDI837Parser()
        result = parser.parse_file(edi_content)
        
        if result['success']:
            print("✅ PARSING SUCCESSFUL!")
            print()
            
            # Display detailed element parsing for first few segments
            print("🔍 DETAILED ELEMENT-LEVEL PARSING:")
            print("=" * 60)
            
            # Show detailed parsing for ISA segment (like in your image)
            if result['detailed_segments']:
                for i, segment in enumerate(result['detailed_segments'][:3]):  # Show first 3 segments
                    print(f"\n📋 {segment['segment_tag']} - {segment['segment_name']}")
                    print("-" * 50)
                    
                    for element in segment['elements']:
                        status = "✅" if element['is_present'] else "❌"
                        value_display = element['value'] if element['value'] else "(empty)"
                        
                        print(f"{status} {element['position']} {element['name']:<35} {value_display:<20}")
                        
                        # Show interpreted value if available
                        if element.get('interpreted_value'):
                            print(f"     └─ Meaning: {element['interpreted_value']}")
                        
                        print(f"     └─ Description: {element['description']}")
                        print()
            
            # Show ISA segment in detail (like your attached image)
            print("\n🎯 ISA SEGMENT DETAILED BREAKDOWN (X12 837 Format):")
            print("=" * 70)
            
            isa_segment = None
            for segment in result['detailed_segments']:
                if segment['segment_tag'] == 'ISA':
                    isa_segment = segment
                    break
            
            if isa_segment:
                print(f"Segment: ISA - {isa_segment['segment_name']}")
                print()
                for element in isa_segment['elements']:
                    pos_str = f"{element['position']}"
                    value_str = element['value'] if element['value'] else "(empty)"
                    meaning_str = element.get('interpreted_value', '')
                    
                    print(f"◯ {element['name']:<40} {pos_str}")
                    if meaning_str:
                        print(f"  {meaning_str:<55} {value_str}")
                    else:
                        print(f"  {value_str}")
                    print()
            
            # Show statistics
            print("📊 ELEMENT PARSING STATISTICS:")
            print("-" * 40)
            total_elements = sum(len(seg['elements']) for seg in result['detailed_segments'])
            present_elements = sum(sum(1 for el in seg['elements'] if el['is_present']) for seg in result['detailed_segments'])
            defined_elements = sum(sum(1 for el in seg['elements'] if 'Element definition not available' not in el['description']) for seg in result['detailed_segments'])
            
            print(f"  Total Elements Parsed: {total_elements}")
            print(f"  Elements with Data: {present_elements}")
            print(f"  Elements with Definitions: {defined_elements}")
            print(f"  Definition Coverage: {(defined_elements/total_elements)*100:.1f}%")
            print(f"  Data Coverage: {(present_elements/total_elements)*100:.1f}%")
            
        else:
            print("❌ PARSING FAILED!")
            print(f"Error: {result['error']}")
    
    except FileNotFoundError:
        print(f"❌ Sample file not found: {sample_file}")
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
    
    print()
    print("🌐 VIEW IN WEB INTERFACE:")
    print("-" * 40)
    print("  1. Start the web app: python app.py")
    print("  2. Open: http://localhost:5000")
    print("  3. Click 'Load Sample' or paste EDI content")
    print("  4. Click 'Element Details' tab to see full breakdown")
    print("  5. Each segment shows position, name, value, and description")

if __name__ == "__main__":
    main()