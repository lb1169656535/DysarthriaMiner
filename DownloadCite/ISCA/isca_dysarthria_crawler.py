import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class CitationScraper:
    def __init__(self):
        self.driver = self._init_browser()
        self.wait = WebDriverWait(self.driver, 20)
        self.results = []

    def _init_browser(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)

    def _click_citation(self):
        try:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            citation_btn = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#show-citation i"))
            )
            self.driver.execute_script("arguments[0].click();", citation_btn)
            content = self.wait.until(
                EC.visibility_of_element_located((By.ID, "citation-content"))
            )
            return content.text
        except Exception as e:
            print(f"抓取失败: {str(e)}")
            return None

    def _save_to_file(self):
        with open('citations.csv', 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['URL', 'Citation'])
            writer.writerows(self.results)

    def scrape(self, urls):
        try:
            for idx, url in enumerate(urls, 1):
                print(f"正在处理 [{idx}/{len(urls)}]: {url}")
                self.driver.get(url)
                time.sleep(1)
                
                if citation := self._click_citation():
                    self.results.append((url, citation))
                
                if idx % 10 == 0:
                    self._save_to_file()
        finally:
            self._save_to_file()
            self.driver.quit()
            print(f"完成！成功获取 {len(self.results)}/{len(urls)} 条记录")

if __name__ == "__main__":
    sample_urls = [
        "https://www.isca-archive.org/icslp_1996/menendezpidal96_icslp.html",
        "https://www.isca-archive.org/maveba_1999/tomik99_maveba.html",
        "https://www.isca-archive.org/icslp_2002/patel02_icslp.html",
        "https://www.isca-archive.org/icslp_2002/will02_icslp.html",
        "https://www.isca-archive.org/speechprosody_2002/claen02_speechprosody.html",
        "https://www.isca-archive.org/maveba_2003/niu03_maveba.html",
        "https://www.isca-archive.org/ssw_2004/kain04_ssw.html",
        "https://www.isca-archive.org/interspeech_2004/mori04_interspeech.html",
        "https://www.isca-archive.org/interspeech_2004/green04_interspeech.html",
        "https://www.isca-archive.org/interspeech_2007/morales07_interspeech.html",
        "https://www.isca-archive.org/maveba_2007/hernandezdiazhuici07_maveba.html",
        "https://www.isca-archive.org/interspeech_2008/carmichael08_interspeech.html",
        "https://www.isca-archive.org/interspeech_2009/nagaraja09_interspeech.html",
        "https://www.isca-archive.org/interspeech_2009/sharma09_interspeech.html",
        "https://www.isca-archive.org/interspeech_2010/kim10i_interspeech.html",
        "https://www.isca-archive.org/interspeech_2010/hosom10_interspeech.html",
        "https://www.isca-archive.org/speechprosody_2010/kim10_speechprosody.html",
        "https://www.isca-archive.org/interspeech_2011/shimura11_interspeech.html",
        "https://www.isca-archive.org/interspeech_2011/hummel11_interspeech.html",
        "https://www.isca-archive.org/maveba_2011/skodda11_maveba.html",
        "https://www.isca-archive.org/maveba_2011/rusz11_maveba.html",
        "https://www.isca-archive.org/interspeech_2012/paja12_interspeech.html",
        "https://www.isca-archive.org/interspeech_2012/kim12d_interspeech.html",
        "https://www.isca-archive.org/spasr_2013/rudzicz13_spasr.html",
        "https://www.isca-archive.org/interspeech_2013/kim13d_interspeech.html",
        "https://www.isca-archive.org/interspeech_2013/martinez13b_interspeech.html",
        "https://www.isca-archive.org/interspeech_2013/antolik13_interspeech.html",
        "https://www.isca-archive.org/interspeech_2014/berry14_interspeech.html",
        "https://www.isca-archive.org/interspeech_2015/wong15_interspeech.html",
        "https://www.isca-archive.org/interspeech_2015/bigi15_interspeech.html",
        "https://www.isca-archive.org/slpat_2016/prakash16_slpat.html",
        "https://www.isca-archive.org/slpat_2016/aihara16_slpat.html",
        "https://www.isca-archive.org/interspeech_2016/bhat16_interspeech.html",
        "https://www.isca-archive.org/interspeech_2016/kim16c_interspeech.html",
        "https://www.isca-archive.org/interspeech_2017/vachhani17_interspeech.html",
        "https://www.isca-archive.org/interspeech_2017/gillespie17_interspeech.html",
        "https://www.isca-archive.org/interspeech_2017/novotny17_interspeech.html",
        "https://www.isca-archive.org/interspeech_2018/np18_interspeech.html",
        "https://www.isca-archive.org/interspeech_2018/vasquezcorrea18_interspeech.html",
        "https://www.isca-archive.org/interspeech_2018/kim18e_interspeech.html",
        "https://www.isca-archive.org/interspeech_2019/shor19_interspeech.html",
        "https://www.isca-archive.org/interspeech_2019/rueda19_interspeech.html",
        "https://www.isca-archive.org/interspeech_2019/hu19c_interspeech.html",
        "https://www.isca-archive.org/interspeech_2019/korzekwa19_interspeech.html",
        "https://www.isca-archive.org/interspeech_2019/liu19j_interspeech.html",
        "https://www.isca-archive.org/interspeech_2019/mayle19_interspeech.html",
        "https://www.isca-archive.org/interspeech_2020/hernandez20_interspeech.html",
        "https://www.isca-archive.org/interspeech_2020/chen20s_interspeech.html",
        "https://www.isca-archive.org/interspeech_2020/tong20b_interspeech.html",
        "https://www.isca-archive.org/interspeech_2020/alhinti20_interspeech.html",
        "https://www.isca-archive.org/interspeech_2020/kodrasi20_interspeech.html",
        "https://www.isca-archive.org/speechprosody_2020/fivela20_speechprosody.html",
        "https://www.isca-archive.org/isaph_2021/sansegundo21_isaph.html",
        "https://www.isca-archive.org/interspeech_2021/vasquezcorrea21_interspeech.html",
        "https://www.isca-archive.org/interspeech_2021/wang21u_interspeech.html",
        "https://www.isca-archive.org/interspeech_2022/turrisi22_interspeech.html",
        "https://www.isca-archive.org/interspeech_2022/salim22_interspeech.html",
        "https://www.isca-archive.org/interspeech_2022/zhang22o_interspeech.html",
        "https://www.isca-archive.org/interspeech_2022/abderrazek22_interspeech.html",
        "https://www.isca-archive.org/interspeech_2022/hernandez22_interspeech.html",
        "https://www.isca-archive.org/interspeech_2022/tran22c_interspeech.html",
        "https://www.isca-archive.org/ssw_2023/fong23b_ssw.html",
        "https://www.isca-archive.org/interspeech_2023/venkatathirumalakumar23_interspeech.html",
        "https://www.isca-archive.org/interspeech_2023/bhattacharjee23_interspeech.html",
        "https://www.isca-archive.org/interspeech_2023/svihlik23_interspeech.html",
        "https://www.isca-archive.org/interspeech_2023/illner23_interspeech.html",
        "https://www.isca-archive.org/interspeech_2023/rathod23_interspeech.html",
        "https://www.isca-archive.org/interspeech_2023/riosurrego23_interspeech.html",
        "https://www.isca-archive.org/interspeech_2023/hermann23_interspeech.html",
        "https://www.isca-archive.org/speechprosody_2024/fernandez24_speechprosody.html",
        "https://www.isca-archive.org/issp_2024/munasinghe24_issp.html",
        "https://www.isca-archive.org/interspeech_2024/lin24e_interspeech.html",
        "https://www.isca-archive.org/interspeech_2024/gao24c_interspeech.html",
        "https://www.isca-archive.org/interspeech_2024/samptur24_interspeech.html",
        "https://www.isca-archive.org/interspeech_2024/zhang24l_interspeech.html",
        "https://www.isca-archive.org/interspeech_2024/xiong24_interspeech.html",
        "https://www.isca-archive.org/interspeech_2024/wan24b_interspeech.html",
        "https://www.isca-archive.org/interspeech_2024/leung24_interspeech.html",
        "https://www.isca-archive.org/interspeech_2024/zaheera24_interspeech.html"
    ]
    
    scraper = CitationScraper()
    scraper.scrape(sample_urls)
