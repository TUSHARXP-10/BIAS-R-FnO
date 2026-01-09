import requests
import os

def test_generate_report():
    url = 'http://localhost:5000/api/reports/generate'
    payload = {
        'symbol': 'BANKNIFTY',
        'period': '3mo'
    }
    headers = {'Content-Type': 'application/json'}

    try:
        print(f"Sending request to {url}...")
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                report_path = data.get('report_path')
                print(f"Report generated successfully: {report_path}")
                if report_path and os.path.exists(report_path):
                    print("✅ PDF file exists.")
                    print(f"Chart path: {data['data'].get('chart_path')}")
                else:
                    print("❌ PDF file NOT found.")
            else:
                print("❌ API returned success=False")
                print(data)
        else:
            print(f"❌ Request failed with status code {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Is it running?")

if __name__ == "__main__":
    test_generate_report()
