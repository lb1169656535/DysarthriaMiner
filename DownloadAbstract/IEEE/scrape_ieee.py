from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import csv
import os
import random
import logging
import hashlib
from urllib.parse import urljoin, urlencode

# ------------------------- 全局配置 -------------------------
CONFIG = {
    "BASE_URL": "https://ieeexplore.ieee.org",
    "SEARCH_PATH": "/search/searchresult.jsp",
    "QUERY_PARAMS": {
        "newsearch": "true",
        "queryText": "Dysarthria"
    },
    "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "REQUEST_DELAY": (3, 8),
    "MAX_RETRIES": 5,
    "PAGE_LOAD_TIMEOUT": 60,
    "HEADLESS_MODE": False,
    "MAX_PAGES": 100,
    "BROWSER_RESTART_INTERVAL": 5
}

# ------------------------- 日志配置 -------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('crawler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class SmartBrowser:
    def __init__(self):
        self.driver = self._create_driver()
        self.page_hash_history = []
    
    def _create_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument(f"user-agent={CONFIG['USER_AGENT']}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        if CONFIG["HEADLESS_MODE"]:
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")

        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)

    def restart(self):
        self.driver.quit()
        self.driver = self._create_driver()
        self.page_hash_history = []
        logging.info("浏览器实例已重启")

class PaginationEngine:
    def __init__(self, browser):
        self.browser = browser
        self.current_page = 1
        self.last_page_content = ""
    
    def navigate_initial_page(self, url):
        for _ in range(CONFIG["MAX_RETRIES"]):
            try:
                self.browser.driver.get(url)
                self.wait_for_page_ready()
                if self.handle_cookies():
                    return True
            except TimeoutException:
                logging.warning("初始页面加载超时，重试中...")
        return False

    def handle_cookies(self):
        cookie_selectors = [
            ("id", "onetrust-accept-btn-handler"),
            ("css selector", "button.cookie-btn"),
            ("xpath", "//button[contains(text(),'Accept')]")
        ]
        
        for by, value in cookie_selectors:
            try:
                btn = WebDriverWait(self.browser.driver, 3).until(
                    EC.element_to_be_clickable((by, value))
                )
                btn.click()
                logging.info("Cookie弹窗已接受")
                return True
            except TimeoutException:
                continue
        return False

    def wait_for_page_ready(self):
        try:
            WebDriverWait(self.browser.driver, CONFIG["PAGE_LOAD_TIMEOUT"]).until(
                lambda d: d.execute_script("return document.readyState") == 'complete' and
                          d.execute_script("return jQuery.active == 0") and
                          len(d.find_elements(By.CSS_SELECTOR, "div.List-results-items")) > 0
            )
        except TimeoutException:
            logging.warning("页面加载超时，继续执行")

    def get_paper_ids(self):
        try:
            WebDriverWait(self.browser.driver, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div[class^='List-results']")
                )
            )
            soup = BeautifulSoup(self.browser.driver.page_source, 'html.parser')
            return [div['id'] for div in soup.find_all('div', class_=lambda x: x and x.startswith('List-results'))]
        except TimeoutException:
            logging.error("论文列表加载失败")
            return []

    def handle_pagination(self):
        current_retry = 0
        initial_hash = self._page_fingerprint()
        
        while current_retry < CONFIG["MAX_RETRIES"]:
            try:
                next_btn = WebDriverWait(self.browser.driver, 15).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(@class, 'stats-Pagination_arrow') and not(@disabled)]")
                    )
                )
                
                # 可视化反馈
                self.browser.driver.execute_script(
                    "arguments[0].style.boxShadow = '0 0 8px rgba(255,0,0,0.5)';", next_btn)
                
                # 滚动到视图
                self.browser.driver.execute_script(
                    "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", next_btn)
                
                # 点击前延迟
                time.sleep(random.uniform(0.5, 1.2))
                
                # 执行点击
                self.browser.driver.execute_script("arguments[0].click();", next_btn)
                
                # 双重验证
                WebDriverWait(self.browser.driver, 20).until(
                    lambda d: 
                    self._page_fingerprint() != initial_hash and
                    len(d.find_elements(By.CSS_SELECTOR, "div[class^='List-results']")) > 0
                )
                
                self.current_page += 1
                logging.info(f"成功跳转到第 {self.current_page} 页")
                return True
                
            except TimeoutException as e:
                current_retry += 1
                logging.warning(f"分页失败，尝试 #{current_retry}")
                self.browser.driver.refresh()
                self.wait_for_page_ready()
        
        logging.error("分页操作达到最大重试次数")
        return False

    def _page_fingerprint(self):
        """生成页面特征指纹"""
        elements = self.browser.driver.find_elements(
            By.CSS_SELECTOR, "div[class^='List-results'] > div")
        return hashlib.md5(
            "|".join([el.get_attribute("id") for el in elements]).encode()
        ).hexdigest()

class DataManager:
    def __init__(self):
        self.crawled_ids = set()
        self._init_output()
        
    def _init_output(self):
        if not os.path.exists("papers.csv"):
            with open("papers.csv", "w", newline="", encoding="utf-8") as f:
                csv.DictWriter(f, fieldnames=["id", "title", "abstract", "date"]).writeheader()
    
    def save_paper(self, paper_data):
        if paper_data["id"] in self.crawled_ids:
            return False
            
        with open("papers.csv", "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "title", "abstract", "date"])
            writer.writerow(paper_data)
        
        self.crawled_ids.add(paper_data["id"])
        return True

def main():
    browser = SmartBrowser()
    pagination = PaginationEngine(browser)
    data_manager = DataManager()
    
    try:
        # 初始化搜索页面
        search_url = urljoin(CONFIG["BASE_URL"], CONFIG["SEARCH_PATH"]) + "?" + urlencode(CONFIG["QUERY_PARAMS"])
        if not pagination.navigate_initial_page(search_url):
            logging.error("无法加载初始页面")
            return

        while pagination.current_page <= CONFIG["MAX_PAGES"]:
            # 浏览器维护
            if pagination.current_page % CONFIG["BROWSER_RESTART_INTERVAL"] == 0:
                browser.restart()
                pagination.navigate_initial_page(search_url)
            
            logging.info(f"正在处理第 {pagination.current_page} 页")
            
            # 获取论文列表
            paper_ids = pagination.get_paper_ids()
            if not paper_ids:
                logging.warning("未找到论文列表，终止爬取")
                break
                
            # 处理每篇论文
            success_count = 0
            for idx, pid in enumerate(paper_ids, 1):
                with browser.driver.context(browser.driver.CONTEXT_CHROME):
                    paper_data = parse_single_paper(browser.driver, pid)
                    if paper_data and data_manager.save_paper(paper_data):
                        success_count += 1
                        logging.info(f"({idx}/{len(paper_ids)}) 已保存: {paper_data['title'][:30]}...")
                        random_delay()
            
            logging.info(f"本页完成: {success_count}/{len(paper_ids)}")
            
            # 分页操作
            if not pagination.handle_pagination():
                logging.info("到达最后一页")
                break

    except Exception as e:
        logging.error(f"程序异常终止: {str(e)}")
    finally:
        browser.driver.quit()
        logging.info(f"数据已保存至 {os.path.abspath('papers.csv')}")

def parse_single_paper(driver, paper_id):
    original_window = driver.current_window_handle
    try:
        driver.switch_to.new_window('tab')
        driver.get(f"{CONFIG['BASE_URL']}/document/{paper_id}")
        
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1.document-title"))
        )
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        return {
            "id": paper_id,
            "title": soup.find('h1', class_='document-title').get_text(strip=True),
            "abstract": soup.find('div', {'xplmathjax': True}).get_text(strip=True),
            "date": soup.find('div', class_='doc-abstract-dateadded').get_text(strip=True).split(":")[1].strip()
        }
    except Exception as e:
        logging.error(f"解析失败 [{paper_id}]: {str(e)}")
        return None
    finally:
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(original_window)

def random_delay():
    time.sleep(random.uniform(*CONFIG["REQUEST_DELAY"]))

if __name__ == "__main__":
    main()
