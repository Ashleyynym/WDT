#!/usr/bin/env python3
"""
Test script to check Google Sheets data
"""

import requests
import csv
import io

def test_google_sheet():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRDvTYjmphSWhboVSZ0f0etf4h4O-8jxUFjfcd6GsarXZGAtZSCr_YD0r8e0JWfAJxBLtpuO4sTDzU1/pub?output=csv"
    
    try:
        print(f"Testing URL: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        print(f"Status Code: {response.status_code}")
        print(f"Content Length: {len(response.text)} characters")
        print("\nFirst 500 characters of content:")
        print("-" * 50)
        print(response.text[:500])
        print("-" * 50)
        
        # Try to parse as CSV
        try:
            csv_reader = csv.DictReader(io.StringIO(response.text))
            print(f"\nCSV Headers: {csv_reader.fieldnames}")
            
            # Show first few rows
            print("\nFirst 3 rows:")
            for i, row in enumerate(csv_reader):
                if i >= 3:
                    break
                print(f"Row {i+1}: {dict(row)}")
                
        except Exception as csv_error:
            print(f"Error parsing CSV: {csv_error}")
            
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    test_google_sheet() 