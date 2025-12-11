#!/usr/bin/env python3
"""
Test script to demonstrate EDI 837 and EDI 820 parsing capabilities
"""

from edi_parser import UniversalEDIParser
import json

def test_edi_837():
    """Test EDI 837 parsing"""
    print("=" * 60)
    print("TESTING EDI 837 - HEALTHCARE CLAIMS")
    print("=" * 60)
    
    with open('sample_edi_837.txt', 'r') as f:
        content = f.read()
    
    parser = UniversalEDIParser()
    result = parser.parse_file(content)
    
    if result['success']:
        data = result['data']
        summary = parser.get_data_summary()
        
        print(f"✅ Transaction Type: {result['transaction_type']}")
        print(f"📊 Total Segments: {len(result['segments'])}")
        print(f"🏥 Claims: {len(data.get('claims', []))}")
        print(f"👨‍⚕️ Providers: {len(data.get('providers', []))}")
        print(f"👤 Patients: {len(data.get('patients', []))}")
        print(f"💰 Total Claim Amount: ${summary['amounts'].get('total_claim_amount', 0)}")
        print(f"📋 Service Lines: {summary['counts'].get('total_service_lines', 0)}")
        
        if data.get('claims'):
            claim = data['claims'][0]
            print(f"\n📋 Sample Claim:")
            print(f"   ID: {claim.get('claim_id', 'N/A')}")
            print(f"   Amount: ${claim.get('claim_amount', 'N/A')}")
            print(f"   Service Lines: {len(claim.get('service_lines', []))}")
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")

def test_edi_820():
    """Test EDI 820 parsing"""
    print("\n" + "=" * 60)
    print("TESTING EDI 820 - PAYMENT/REMITTANCE ADVICE")
    print("=" * 60)
    
    with open('sample_edi_820.txt', 'r') as f:
        content = f.read()
    
    parser = UniversalEDIParser()
    result = parser.parse_file(content)
    
    if result['success']:
        data = result['data']
        summary = parser.get_data_summary()
        
        print(f"✅ Transaction Type: {result['transaction_type']}")
        print(f"📊 Total Segments: {len(result['segments'])}")
        print(f"💳 Payers: {len(data.get('payers', []))}")
        print(f"🏢 Payees: {len(data.get('payees', []))}")
        print(f"💰 Total Payment Amount: ${summary['amounts'].get('total_payment_amount', 0)}")
        print(f"📋 Remittances: {len(data.get('remittance_data', []))}")
        print(f"⚕️ Service Payments: {len(data.get('service_payments', []))}")
        print(f"⚠️ Adjustments: {len(data.get('adjustments', []))}")
        
        payment_info = data.get('payment_info', {})
        if payment_info:
            print(f"\n💳 Payment Information:")
            print(f"   Method: {payment_info.get('payment_method', 'N/A')}")
            print(f"   Credit/Debit: {payment_info.get('credit_debit_flag', 'N/A')}")
            print(f"   Account: {payment_info.get('account_number', 'N/A')}")
        
        if data.get('remittance_data'):
            rmr = data['remittance_data'][0]
            print(f"\n📋 Sample Remittance:")
            print(f"   Reference: {rmr.get('reference_id', 'N/A')}")
            print(f"   Payment: ${rmr.get('payment_amount', 'N/A')}")
            print(f"   Adjustment: ${rmr.get('adjustment_amount', 'N/A')}")
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")

def test_web_endpoints():
    """Test web application endpoints"""
    print("\n" + "=" * 60)
    print("TESTING WEB APPLICATION ENDPOINTS")
    print("=" * 60)
    
    import requests
    import time
    
    # Start Flask app in background
    import subprocess
    import signal
    import os
    
    try:
        # Start the Flask app
        proc = subprocess.Popen(['python', 'app.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(3)  # Give it time to start
        
        # Test EDI 837 endpoint
        try:
            response = requests.get('http://localhost:5000/sample', timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ EDI 837 Endpoint: SUCCESS")
                print(f"   Transaction Type: {data.get('transaction_type', 'N/A')}")
            else:
                print(f"❌ EDI 837 Endpoint: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ EDI 837 Endpoint: {str(e)}")
        
        # Test EDI 820 endpoint
        try:
            response = requests.get('http://localhost:5000/sample820', timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ EDI 820 Endpoint: SUCCESS")
                print(f"   Transaction Type: {data.get('transaction_type', 'N/A')}")
            else:
                print(f"❌ EDI 820 Endpoint: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ EDI 820 Endpoint: {str(e)}")
        
    except Exception as e:
        print(f"❌ Web App Test Failed: {str(e)}")
    finally:
        # Clean up
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except:
            try:
                proc.kill()
            except:
                pass

if __name__ == '__main__':
    test_edi_837()
    test_edi_820()
    test_web_endpoints()
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED!")
    print("🎉 EDI Parser now supports both EDI 837 and EDI 820!")
    print("=" * 60)