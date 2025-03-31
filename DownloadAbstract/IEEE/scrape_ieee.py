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
    "REQUEST_DELAY": (1, 3),       # 随机请求延迟范围（秒）
    "MAX_RETRIES": 3,              # 最大重试次数
    "PAGE_LOAD_TIMEOUT": 60,       # 页面加载超时时间（秒）
    "HEADLESS_MODE": False,        # 无头模式开关
    "RESOURCE_BLOCK_TYPES": [      # 屏蔽的资源类型
        "image", "stylesheet", "font", "media" 
    ]
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

# ------------------------- 浏览器工具类 -------------------------
class BrowserManager:
    @staticmethod
    def create_driver():
        """创建优化配置的浏览器实例"""
        options = webdriver.ChromeOptions()
        
        # 基础配置
        options.add_argument(f"user-agent={CONFIG['USER_AGENT']}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        
        # 资源加载控制
        options.add_experimental_option("prefs", {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.stylesheet": 2
        })
        
        # SSL/网络配置
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--allow-insecure-localhost")
        
        # 无头模式
        if CONFIG["HEADLESS_MODE"]:
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
        
        # 初始化驱动
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.set_page_load_timeout(CONFIG["PAGE_LOAD_TIMEOUT"])
            driver.set_script_timeout(30)
            return driver
        except WebDriverException as e:
            logging.error(f"浏览器初始化失败: {str(e)}")
            raise

# ------------------------- 爬虫核心类 -------------------------
class IEEECrawler:
    def __init__(self, driver):
        self.driver = driver
        self.current_page = 1
    
    def safe_get(self, url, max_retries=3):
        """带重试机制的页面加载"""
        for attempt in range(max_retries):
            try:
                self.driver.get(url)
                self.wait_for_page_ready()
                return True
            except TimeoutException:
                logging.warning(f"页面加载超时（尝试 {attempt+1}/{max_retries}）")
                if attempt < max_retries - 1:
                    self.driver.execute_script("window.stop();")
                    self.driver.refresh()
        return False

    def wait_for_page_ready(self, timeout=30):
        """等待页面完全就绪"""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except TimeoutException:
            logging.warning("页面就绪状态检测超时")

    def handle_cookies(self):
        """三重Cookie处理机制"""
        # 方法1：常规点击
        try:
            btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            )
            btn.click()
            logging.info("Cookie弹窗已接受")
            return True
        except TimeoutException:
            pass
        
        # 方法2：JavaScript执行
        try:
            self.driver.execute_script(
                "document.getElementById('onetrust-accept-btn-handler')?.click()"
            )
            logging.info("通过JS点击Cookie按钮")
            return True
        except:
            pass
        
        # 方法3：强制跳过
        logging.warning("Cookie弹窗处理失败，尝试继续运行")
        return False

    def get_paper_ids(self):
        """获取当前页论文ID列表（带重试）"""
        for attempt in range(CONFIG["MAX_RETRIES"]):
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//div[contains(@class, "List-results-items")]')
                    )
                )
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                return [div['id'] for div in soup.find_all('div', class_='List-results-items')]
            except TimeoutException:
                logging.warning(f"论文列表加载失败（尝试 {attempt+1}）")
                if attempt < CONFIG["MAX_RETRIES"] - 1:
                    self.driver.refresh()
        return []

    def parse_paper_detail(self, paper_id):
        """解析论文详情（带异常熔断）"""
        original_window = self.driver.current_window_handle
        
        try:
            # 新标签页打开
            self.driver.switch_to.new_window('tab')
            self.safe_get(f"{CONFIG['BASE_URL']}/document/{paper_id}")
            
            # 等待核心内容
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1.document-title"))
            )
            
            # 解析数据
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            title = soup.find('h1', class_='document-title').get_text(strip=True)
            abstract = soup.find('div', {'xplmathjax': True}).get_text(strip=True)
            date = soup.find('div', class_='doc-abstract-dateadded').get_text(strip=True).split(":")[1].strip()
            
            return {
                "id": paper_id,
                "title": title,
                "abstract": abstract,
                "date": date
            }
        except Exception as e:
            logging.error(f"论文解析失败: {str(e)}")
            return None
        finally:
            if len(self.driver.window_handles) > 1:
                self.driver.close()
                self.driver.switch_to.window(original_window)
            time.sleep(random.uniform(*CONFIG["REQUEST_DELAY"]))

    def handle_pagination(self):
        """智能分页控制器"""
        for attempt in range(CONFIG["MAX_RETRIES"]):
            try:
                # 复合定位条件
                next_btn = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, '//button[contains(@class, "stats-Pagination_arrow") and not(@disabled)]')
                    )
                )
                
                # 滚动到可视区域
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                    next_btn
                )
                
                # 点击前状态验证
                if not next_btn.is_enabled():
                    logging.info("分页按钮不可用")
                    return False
                
                next_btn.click()
                
                # 等待新内容加载
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//div[contains(@class, "List-results-items")]')
                    )
                )
                return True
            except TimeoutException:
                logging.warning(f"分页操作失败（尝试 {attempt+1}）")
                if attempt < CONFIG["MAX_RETRIES"] - 1:
                    self.driver.refresh()
        return False

# ------------------------- 主程序 -------------------------
def main():
    driver = BrowserManager.create_driver()
    crawler = IEEECrawler(driver)
    
    try:
        # 初始化数据文件
        with open('papers.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'title', 'abstract', 'date'])
            writer.writeheader()
        
        # 构建搜索URL
        search_url = urljoin(CONFIG["BASE_URL"], CONFIG["SEARCH_PATH"]) + "?" + urlencode(CONFIG["QUERY_PARAMS"])
        if not crawler.safe_get(search_url):
            logging.error("初始页面加载失败")
            return
        
        # 处理Cookie
        if not crawler.handle_cookies():
            logging.warning("可能影响后续操作")
        
        # 主爬取循环
        while True:
            logging.info(f"正在处理第 {crawler.current_page} 页")
            
            paper_ids = crawler.get_paper_ids()
            if not paper_ids:
                logging.error("未找到论文列表，终止爬取")
                break
                
            # 详情页处理
            success_count = 0
            for pid in paper_ids:
                paper_data = crawler.parse_paper_detail(pid)
                if paper_data:
                    with open('papers.csv', 'a', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=['id', 'title', 'abstract', 'date'])
                        writer.writerow(paper_data)
                    success_count += 1
                    logging.info(f"已保存: {paper_data['title'][:30]}...")
            
            logging.info(f"本页成功保存 {success_count}/{len(paper_ids)} 篇论文")
            
            # 分页控制
            if not crawler.handle_pagination():
                logging.info("到达最后一页")
                break
            crawler.current_page += 1
            
    except Exception as e:
        logging.error(f"程序异常终止: {str(e)}")
    finally:
        driver.quit()
        logging.info(f"最终数据已保存至 {os.path.abspath('papers.csv')}")

if __name__ == "__main__":
    main()
