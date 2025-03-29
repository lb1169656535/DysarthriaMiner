from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import csv
import os

# 配置浏览器选项
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

# 初始化浏览器
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

def accept_cookies():
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        ).click()
        print("Cookies accepted")
    except Exception as e:
        print("No cookies banner found")

def get_paper_ids():
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//div[@class="List-results-items"]'))
    )
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    return [div['id'] for div in soup.find_all('div', class_='List-results-items')]

def scrape_paper_details(paper_id):
    driver.execute_script(f"window.open('https://ieeexplore.ieee.org/document/{paper_id}');")
    driver.switch_to.window(driver.window_handles[1])
    
    try:
        # 处理可能的登录弹窗
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'document-title'))
        )
    except:
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        return None, None, None
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # 提取标题
    title = soup.find('h1', class_='document-title').get_text(strip=True) if soup.find('h1', class_='document-title') else 'N/A'
    
    # 提取摘要
    abstract = soup.find('div', {'xplmathjax': True}).get_text(strip=True) if soup.find('div', {'xplmathjax': True}) else 'N/A'
    
    # 提取日期
    date_div = soup.find('div', class_='doc-abstract-dateadded')
    date = date_div.get_text(strip=True).replace('Date Added to IEEE Xplore:', '').strip() if date_div else 'N/A'
    
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    return title, abstract, date

def handle_pagination():
    while True:
        try:
            next_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(@class, "stats-Pagination_arrow_next")]'))
            )
            next_btn.click()
            time.sleep(3)  # 等待页面加载
            return True
        except:
            print("Reached last page")
            return False

def main():
    # 初始化CSV文件
    with open('ieee_papers.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Title', 'Abstract', 'Date Added'])
    
    driver.get("https://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&queryText=Dysarthria")
    accept_cookies()
    time.sleep(2)
    
    while True:
        paper_ids = get_paper_ids()
        print(f"Found {len(paper_ids)} papers on this page")
        
        for pid in paper_ids:
            title, abstract, date = scrape_paper_details(pid)
            if title:
                with open('ieee_papers.csv', 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([pid, title, abstract, date])
                print(f"Saved: {title[:50]}...")
            time.sleep(1)  # 控制请求频率
        
        if not handle_pagination():
            break

    driver.quit()
    print("所有数据已保存到:", os.path.abspath('ieee_papers.csv'))

if __name__ == "__main__":
    main()
