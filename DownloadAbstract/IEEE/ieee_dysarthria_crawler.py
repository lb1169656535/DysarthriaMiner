import csv
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class IEEECrawler:
    def __init__(self):
        self.driver = self._init_browser()
        self.wait = WebDriverWait(self.driver, 20)
    
    def _init_browser(self):
        """初始化浏览器配置"""
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)

    def crawl_paper_ids(self):
        """第一步：爬取所有论文ID"""
        base_url = "https://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&queryText=Dysarthria&highlight=true&returnType=SEARCH&matchPubs=true&pageNumber={}&returnFacets=ALL&rowsPerPage=100"
        
        with open('paper_ids.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['PaperID'])
            
            for page in range(1, 6):  # 爬取前5页
                self.driver.get(base_url.format(page))
                time.sleep(2)
                
                # 定位结果容器
                results_container = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, '//xpl-results-list'))
                )
                
                # 获取所有论文条目
                items = results_container.find_elements(By.XPATH, './/div[contains(@class, "List-results-items")]')
                for item in items:
                    paper_id = item.get_attribute('id')
                    if paper_id.isdigit():
                        writer.writerow([paper_id])
                print(f"第 {page} 页ID抓取完成")

    def parse_paper_details(self, paper_id):
        """第二步：解析论文详情"""
        self.driver.get(f"https://ieeexplore.ieee.org/document/{paper_id}")
        
        try:
            # 点击Cite按钮
            cite_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(., "Cite This")]'))
            )
            self.driver.execute_script("arguments[0].click();", cite_btn)
            time.sleep(1)
            
            # 勾选复选框
            checkbox = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//input[@type="checkbox"]'))
            )
            self.driver.execute_script("arguments[0].click();", checkbox)
            time.sleep(1)
            
            # 提取文本内容
            text_div = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="text" and @xplmathjax]'))
            )
            parts = [p.strip() for p in text_div.text.split('\n') if p.strip()]
            
            # 解析各部分数据
            citation = parts[0]
            title = re.search(r'"(.+?)"', citation).group(1)
            abstract = parts[1].replace("Abstract: ", "")
            keywords = parts[2].replace("Keywords: ", "")
            links = ';'.join([a.get_attribute('href') for a in text_div.find_elements(By.TAG_NAME, 'a')])
            
            return {
                'Title': title,
                'Abstract': abstract,
                'Keywords': keywords,
                'Links': links,
                'Citation': citation
            }
            
        except Exception as e:
            print(f"解析论文 {paper_id} 失败: {str(e)}")
            return None

    def crawl_metadata(self):
        """执行元数据抓取"""
        with open('paper_ids.csv') as f:
            reader = csv.reader(f)
            next(reader)  # 跳过标题
            paper_ids = [row[0] for row in reader]
        
        with open('paper_metadata.csv', 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Title', 'Abstract', 'Keywords', 'Links', 'Citation']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for idx, pid in enumerate(paper_ids, start=224):
                print(f"正在处理第 {idx}/{len(paper_ids)} 篇论文")
                if data := self.parse_paper_details(pid):
                    writer.writerow(data)
    
    def close(self):
        self.driver.quit()

if __name__ == "__main__":
    crawler = IEEECrawler()
    
    # 第一步：抓取ID
   # crawler.crawl_paper_ids()
    
    # 第二步：抓取元数据
    crawler.crawl_metadata()
    
    crawler.close()