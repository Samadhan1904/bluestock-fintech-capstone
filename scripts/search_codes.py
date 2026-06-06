# search_codes.py
# Quick script to find correct AMFI scheme codes from mfapi.in

import requests

funds = [
    "HDFC Top 100",
    "SBI Bluechip",
    "ICICI Bluechip",
    "Nippon Large Cap",
    "Axis Bluechip",
    "Kotak Bluechip"
]

for fund in funds:
    query = fund.replace(" ", "+")
    url = "https://api.mfapi.in/mf/search?q=" + query
    
    try:
        res = requests.get(url, timeout=10)
        results = res.json()
        
        print("\n--- " + fund + " ---")
        for r in results[:3]:
            code = r["schemeCode"]
            name = r["schemeName"]
            print("  Code: " + str(code) + "  |  " + name)
    
    except Exception as e:
        print("Error for " + fund + ": " + str(e))

