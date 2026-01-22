import requests
import pytest
import time

@pytest.mark.parametrize("symbol", ["RELIANCE.NS", "TCS.NS", "INFY.NS"])
def test_symbol(symbol):
    url = 'http://localhost:5000/api/reports/generate'
    payload = {
        'symbol': symbol,
        'period': '3mo'
    }
    headers = {'Content-Type': 'application/json'}
    
    print(f"\nTesting symbol: {symbol}...")
    try:
        start_time = time.time()
        response = requests.post(url, json=payload, headers=headers)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"✅ Success ({duration:.2f}s)")
                print(f"   Report: {data['report_path']}")
                print(f"   Price: {data['data']['indicators']['current_price']}")
            else:
                print(f"❌ Failed: API returned success=False")
                print(data)
        else:
            print(f"❌ Failed: Status Code {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_invalid_symbol():
    print("\nTesting INVALID symbol (FAKESYMBOL)...")
    url = 'http://localhost:5000/api/reports/generate'
    payload = {'symbol': 'FAKESYMBOL', 'period': '3mo'}
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
             # Expecting 400 or 500, but hopefully handled gracefully
             print(f"✅ Correctly handled invalid symbol (Status: {response.status_code})")
             print(f"   Response: {response.text}")
        else:
            data = response.json()
            if not data.get('success'):
                print(f"✅ Correctly handled invalid symbol (success=False)")
                print(f"   Error: {data.get('error')}")
            else:
                print(f"❌ Unexpected success for FAKESYMBOL")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
