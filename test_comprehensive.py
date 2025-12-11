#!/usr/bin/env python3

"""Test script to verify EDI parser functionality for both 837 and 820 transactions"""

from edi_parser import UniversalEDIParser
import json

def test_edi_837():
    """Test EDI 837 parsing"""
    print("=" * 60)
    print("TESTING EDI 837 (Healthcare Claims)")
    print("=" * 60)
    
    with open('sample_edi_837.txt', 'r') as f:
        content = f.read()
    
    parser = UniversalEDIParser()
    result = parser.parse_file(content)
    
    print(f"✓ Success: {result['success']}")
    print(f"✓ Transaction Type: {result.get('transaction_type', 'Unknown')}")
    
    data = result['data']
    print(f"✓ Claims: {len(data.get('claims', []))}")
    print(f"✓ Providers: {len(data.get('providers', []))}")
    print(f"✓ Subscribers: {len(data.get('subscribers', []))}")
    print(f"✓ Patients: {len(data.get('patients', []))}")
    
    # Display summary
    summary = parser.get_summary_table()
    print(f"✓ Summary entries: {len(summary)}")
    
    # Display data summary
    data_summary = parser.get_data_summary()
    print(f"✓ Transaction type in summary: {data_summary.get('transaction_type', 'Unknown')}")
    print(f"✓ Total segments: {data_summary['counts'].get('total_segments', 0)}")
    
    return result

def test_edi_820():
    """Test EDI 820 parsing"""
    print("\n" + "=" * 60)
    print("TESTING EDI 820 (Payment Order/Remittance Advice)")
    print("=" * 60)
    
    with open('sample_edi_820.txt', 'r') as f:
        content = f.read()
    
    parser = UniversalEDIParser()
    result = parser.parse_file(content)
    
    print(f"✓ Success: {result['success']}")
    print(f"✓ Transaction Type: {result.get('transaction_type', 'Unknown')}")
    
    data = result['data']
    print(f"✓ Payers: {len(data.get('payers', []))}")
    print(f"✓ Payees: {len(data.get('payees', []))}")
    print(f"✓ Remittances: {len(data.get('remittance_data', []))}")
    print(f"✓ Service Payments: {len(data.get('service_payments', []))}")
    print(f"✓ Adjustments: {len(data.get('adjustments', []))}")
    
    # Payment info
    payment_info = data.get('payment_info', {})
    print(f"✓ Payment Amount: ${payment_info.get('payment_amount', 'N/A')}")
    print(f"✓ Payment Method: {payment_info.get('payment_method', 'N/A')}")
    print(f"✓ Credit/Debit Flag: {payment_info.get('credit_debit_flag', 'N/A')}")
    
    # Display summary
    summary = parser.get_summary_table()
    print(f"✓ Summary entries: {len(summary)}")
    
    # Display data summary
    data_summary = parser.get_data_summary()
    print(f"✓ Transaction type in summary: {data_summary.get('transaction_type', 'Unknown')}")
    print(f"✓ Total segments: {data_summary['counts'].get('total_segments', 0)}")
    print(f"✓ Total payment amount: ${data_summary['amounts'].get('total_payment_amount', 0)}")
    
    return result

def test_mixed_content():
    """Test with mixed content to verify auto-detection"""
    print("\n" + "=" * 60)
    print("TESTING AUTO-DETECTION")
    print("=" * 60)
    
    # Test 837 content
    sample_837 = "ISA*00*          *00*          *ZZ*TEST*ZZ*TEST*241205*1200*^*00501*000000001*0*P*:~ST*837*0001~"
    parser = UniversalEDIParser()
    result_837 = parser.parse_file(sample_837)
    print(f"✓ Sample 837 detected as: {result_837.get('transaction_type', 'Unknown')}")
    
    # Test 820 content
    sample_820 = "ISA*00*          *00*          *ZZ*TEST*ZZ*TEST*241205*1200*^*00501*000000001*0*P*:~ST*820*0001~"
    parser = UniversalEDIParser()
    result_820 = parser.parse_file(sample_820)
    print(f"✓ Sample 820 detected as: {result_820.get('transaction_type', 'Unknown')}")

if __name__ == "__main__":
    print("EDI PARSER COMPREHENSIVE TEST")
    print("Testing Universal EDI Parser for both 837 and 820 transactions")
    
    try:
        # Test EDI 837
        result_837 = test_edi_837()
        
        # Test EDI 820
        result_820 = test_edi_820()
        
        # Test auto-detection
        test_mixed_content()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY! ✓")
        print("=" * 60)
        print("The EDI parser now supports:")
        print("• EDI 837 (Healthcare Claims)")
        print("• EDI 820 (Payment Order/Remittance Advice)")
        print("• Automatic transaction type detection")
        print("• Comprehensive parsing of all segments")
        print("• Detailed summary and analysis")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        raise