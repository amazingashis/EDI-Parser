#!/usr/bin/env python3

"""
Demonstration script for Universal EDI Parser
Shows parsing capabilities for both EDI 837 and EDI 820 transactions
"""

from edi_parser import UniversalEDIParser
import json

def demo_edi_837():
    """Demonstrate EDI 837 parsing capabilities"""
    print("🏥 EDI 837 (Healthcare Claims) Demo")
    print("=" * 50)
    
    # Load sample EDI 837
    with open('sample_edi_837.txt', 'r') as f:
        content = f.read()
    
    parser = UniversalEDIParser()
    result = parser.parse_file(content)
    
    if result['success']:
        print(f"✓ Transaction Type: EDI {result['transaction_type']}")
        
        # Show key data
        data = result['data']
        print(f"📊 Claims: {len(data['claims'])}")
        print(f"👨‍⚕️ Providers: {len(data['providers'])}")
        print(f"👤 Subscribers: {len(data['subscribers'])}")
        print(f"🏷️ Segments Parsed: {len(result['segments'])}")
        
        # Show first claim details
        if data['claims']:
            claim = data['claims'][0]
            print(f"\n📄 Claim Details:")
            print(f"   Claim ID: {claim.get('claim_id', 'N/A')}")
            print(f"   Amount: ${claim.get('claim_amount', 'N/A')}")
            print(f"   Service Lines: {len(claim.get('service_lines', []))}")
        
        # Show first provider
        if data['providers']:
            provider = data['providers'][0]
            name = f"{provider.get('name_first', '')} {provider.get('name_last_or_organization', '')}".strip()
            print(f"\n👨‍⚕️ Provider Details:")
            print(f"   Name: {name}")
            print(f"   Type: {provider.get('entity_type_description', 'N/A')}")
            print(f"   ID: {provider.get('id_code', 'N/A')}")
        
    else:
        print(f"❌ Error: {result['error']}")

def demo_edi_820():
    """Demonstrate EDI 820 parsing capabilities"""
    print("\n\n💰 EDI 820 (Payment Order/Remittance Advice) Demo")
    print("=" * 60)
    
    # Load sample EDI 820
    with open('sample_edi_820.txt', 'r') as f:
        content = f.read()
    
    parser = UniversalEDIParser()
    result = parser.parse_file(content)
    
    if result['success']:
        print(f"✓ Transaction Type: EDI {result['transaction_type']}")
        
        # Show key data
        data = result['data']
        print(f"💳 Payers: {len(data['payers'])}")
        print(f"🏥 Payees: {len(data['payees'])}")
        print(f"📋 Remittances: {len(data['remittance_data'])}")
        print(f"🔧 Service Payments: {len(data['service_payments'])}")
        print(f"⚖️ Adjustments: {len(data['adjustments'])}")
        print(f"🏷️ Segments Parsed: {len(result['segments'])}")
        
        # Show payment info
        payment_info = data.get('payment_info', {})
        if payment_info:
            print(f"\n💰 Payment Information:")
            print(f"   Amount: ${payment_info.get('payment_amount', 'N/A')}")
            print(f"   Method: {payment_info.get('payment_method', 'N/A')}")
            print(f"   Credit/Debit: {payment_info.get('credit_debit_flag', 'N/A')}")
            print(f"   Account: {payment_info.get('account_number', 'N/A')}")
        
        # Show first remittance
        if data['remittance_data']:
            rmr = data['remittance_data'][0]
            print(f"\n📋 Remittance Details:")
            print(f"   Reference ID: {rmr.get('reference_id', 'N/A')}")
            print(f"   Payment Amount: ${rmr.get('payment_amount', 'N/A')}")
            print(f"   Action Code: {rmr.get('payment_action_code', 'N/A')}")
        
        # Show payer info
        if data['payers']:
            payer = data['payers'][0]
            name = f"{payer.get('name_first', '')} {payer.get('name_last_or_organization', '')}".strip()
            print(f"\n💳 Payer Details:")
            print(f"   Name: {name}")
            print(f"   ID: {payer.get('id_code', 'N/A')}")
        
        # Show service payment example
        if data['service_payments']:
            svc = data['service_payments'][0]
            print(f"\n🔧 Service Payment Example:")
            print(f"   Service ID: {svc.get('service_id_qualifier', 'N/A')}")
            print(f"   Charge Amount: ${svc.get('charge_amount', 'N/A')}")
            print(f"   Payment Amount: ${svc.get('payment_amount', 'N/A')}")
        
    else:
        print(f"❌ Error: {result['error']}")

def show_auto_detection():
    """Demonstrate automatic transaction type detection"""
    print("\n\n🔍 Auto-Detection Demo")
    print("=" * 30)
    
    # Test with minimal segments
    test_cases = [
        ("EDI 837", "ISA*00*~ST*837*0001~"),
        ("EDI 820", "ISA*00*~ST*820*0001~"),
        ("Unknown", "ISA*00*~ST*999*0001~")  # Unknown transaction type
    ]
    
    for expected, content in test_cases:
        parser = UniversalEDIParser()
        result = parser.parse_file(content)
        
        if result['success']:
            detected = result.get('transaction_type', 'Unknown')
            status = "✓" if detected == expected.split()[-1] else "⚠️"
            print(f"{status} {content[:20]}... → Detected as EDI {detected}")
        else:
            print(f"❌ Failed to parse: {content[:20]}...")

if __name__ == "__main__":
    print("🚀 UNIVERSAL EDI PARSER DEMONSTRATION")
    print("Supporting EDI 837 (Healthcare Claims) & EDI 820 (Payment/Remittance)")
    print("=" * 80)
    
    try:
        # Demo EDI 837
        demo_edi_837()
        
        # Demo EDI 820
        demo_edi_820()
        
        # Demo auto-detection
        show_auto_detection()
        
        print("\n\n🎉 DEMONSTRATION COMPLETE!")
        print("=" * 40)
        print("The Universal EDI Parser successfully handles:")
        print("• EDI 837 (Healthcare Claims)")
        print("• EDI 820 (Payment Order/Remittance Advice)")
        print("• Automatic transaction type detection")
        print("• Comprehensive data extraction and analysis")
        print("\nTo use the web interface, run: python app.py")
        
    except FileNotFoundError as e:
        print(f"❌ Sample file not found: {e}")
        print("Please ensure both sample_edi_837.txt and sample_edi_820.txt are present.")
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        raise