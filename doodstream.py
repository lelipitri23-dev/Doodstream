import logging
import re
import random
import time
from typing import Optional, Tuple
from urllib.parse import urlparse
import cloudscraper
from bs4 import BeautifulSoup

class DoodStreamAPI:
    def __init__(self):
        # cloudscraper akan secara otomatis menangani tantangan Cloudflare
        self.scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        self.logger = logging.getLogger(__name__)
    
    def get_download_url(self, url: str) -> Optional[Tuple[str, str]]:
        # Normalisasi URL ke format embed
        embed_url = url.replace('/d/', '/e/').replace('/f/', '/e/')

        try:
            # 1. Mengakses halaman embed dengan penanganan redirect otomatis
            response = self.scraper.get(embed_url, timeout=30)
            response.raise_for_status()
            
            final_url = response.url
            domain = urlparse(final_url).netloc
            html_content = response.text
            
            # 2. Mencari token pass_md5
            # DoodStream terkadang mengubah pola, kita gunakan regex yang lebih fleksibel
            pass_md5_match = re.search(r'/(pass_md5|pass_md5_extra)/([^"\']+)', html_content)
            
            if not pass_md5_match:
                self.logger.error(f"Gagal menemukan token pass_md5. Panjang HTML: {len(html_content)}")
                return None
            
            pass_path = pass_md5_match.group(1) # pass_md5 atau pass_md5_extra
            pass_id = pass_md5_match.group(2)
            
            # 3. Mendapatkan Base URL Media
            md5_url = f"https://{domain}/{pass_path}/{pass_id}"
            
            # Penting: Referer harus disetel ke URL embed terakhir
            headers = {"Referer": final_url}
            md5_response = self.scraper.get(md5_url, headers=headers)
            media_url_base = md5_response.text

            # 4. Konstruksi Final URL
            token = pass_id.split('/')[-1]
            random_chars = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', k=10))
            
            download_link = f"{media_url_base}{random_chars}?token={token}&expiry={int(time.time())}"

            # 5. Ekstraksi Judul
            soup = BeautifulSoup(html_content, "html.parser")
            title = soup.find("title").text.strip() if soup.find("title") else "Video_Doodstream"
            title = re.sub(r'[\\/*?:"<>|]', "", title)

            return download_link, title

        except Exception as e:
            self.logger.error(f"Error pada DoodStreamAPI: {e}")
            return None
