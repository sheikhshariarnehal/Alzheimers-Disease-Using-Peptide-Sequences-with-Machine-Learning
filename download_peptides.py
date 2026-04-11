import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from typing import List, Dict
import urllib.parse

class PeptideDownloader:
    def __init__(self):
        self.base_url = "https://web.iitm.ac.in/bioinfo2/cpad2/peptides/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.data = []
        self.session = requests.Session()
        
    def fetch_page(self, page_num: int) -> BeautifulSoup:
        """Fetch and parse a single page"""
        try:
            url = f"{self.base_url}?page={page_num}"
            print(f"Fetching page {page_num}...")
            response = self.session.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            print(f"Error fetching page {page_num}: {e}")
            return None
    
    def extract_table_data(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract table data from BeautifulSoup object"""
        records = []
        try:
            table = soup.find('table')
            if not table:
                print("Table not found on page")
                return records
            
            rows = table.find_all('tr')
            
            # Skip header row
            for row in rows[1:]:
                cells = row.find_all('td')
                if len(cells) >= 10:
                    record = {
                        'Entry': cells[0].get_text(strip=True),
                        'Peptide': cells[1].get_text(strip=True),
                        'Length': cells[2].get_text(strip=True),
                        'Class': cells[3].get_text(strip=True),
                        'Protein Name': cells[4].get_text(strip=True),
                        'UniProt ID': cells[5].get_text(strip=True),
                        'Mutant': cells[6].get_text(strip=True),
                        'Reference': cells[7].get_text(strip=True),
                        'PMID': cells[8].get_text(strip=True),
                        'Source Database': cells[9].get_text(strip=True),
                    }
                    records.append(record)
        except Exception as e:
            print(f"Error extracting table data: {e}")
        
        return records
    
    def download_all_pages(self, start_page: int = 1, end_page: int = 68):
        """Download data from all pages"""
        total_records = 0
        
        for page_num in range(start_page, end_page + 1):
            soup = self.fetch_page(page_num)
            if soup:
                records = self.extract_table_data(soup)
                self.data.extend(records)
                total_records += len(records)
                print(f"  ✓ Downloaded {len(records)} records from page {page_num}")
            else:
                print(f"  ✗ Failed to fetch page {page_num}")
            
            # Add delay to avoid overwhelming the server
            time.sleep(0.5)
        
        print(f"\n✓ Total records downloaded: {total_records}")
        return total_records
    
    def save_to_excel(self, filename: str = "peptides_data.xlsx"):
        """Save downloaded data to Excel file"""
        if not self.data:
            print("No data to save")
            return False
        
        try:
            df = pd.DataFrame(self.data)
            df.to_excel(filename, index=False, sheet_name='Peptides')
            print(f"✓ Data saved to {filename}")
            
            # Print summary
            print(f"\nSummary:")
            print(f"  Total records: {len(df)}")
            print(f"  Columns: {list(df.columns)}")
            print(f"  Amyloid: {len(df[df['Class'] == 'Amyloid'])}")
            print(f"  Non-amyloid: {len(df[df['Class'] == 'Non-amyloid'])}")
            
            return True
        except Exception as e:
            print(f"Error saving to Excel: {e}")
            return False
    
    def save_to_csv(self, filename: str = "peptides_data.csv"):
        """Save downloaded data to CSV file"""
        if not self.data:
            print("No data to save")
            return False
        
        try:
            df = pd.DataFrame(self.data)
            df.to_csv(filename, index=False)
            print(f"✓ Data saved to {filename}")
            return True
        except Exception as e:
            print(f"Error saving to CSV: {e}")
            return False


def main():
    print("=" * 70)
    print("CPAD 2.0 Peptide Database Downloader")
    print("=" * 70)
    
    downloader = PeptideDownloader()
    
    # Download all pages from 1 to 68
    print("\nStarting download of all 68 pages...")
    print("-" * 70)
    total = downloader.download_all_pages(start_page=1, end_page=68)
    
    # Save results
    print("\n" + "-" * 70)
    print("Saving data to files...")
    
    output_dir = "."  # Current directory
    
    # Save to both Excel and CSV
    downloader.save_to_excel(f"{output_dir}/peptides_data.xlsx")
    downloader.save_to_csv(f"{output_dir}/peptides_data.csv")
    
    print("\n" + "=" * 70)
    print("✓ Download completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
