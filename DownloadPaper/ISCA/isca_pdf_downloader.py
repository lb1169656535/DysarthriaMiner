import os
import time
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

# 配置参数
DOWNLOAD_DIR = "paper_pdfs"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
REQUEST_DELAY = 2  # 每次请求间隔秒数

def setup_download_dir():
    """创建下载目录"""
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_pdf(url):
    """处理单个论文页面的PDF下载"""
    try:
        # 获取论文页面
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        
        # 解析PDF链接
        soup = BeautifulSoup(response.text, 'html.parser')
        pdf_link = soup.find('a', href=lambda href: href and href.endswith('.pdf'))
        
        if not pdf_link:
            print(f"未找到PDF链接: {url}")
            return

        # 构建完整PDF URL
        pdf_url = urljoin(url, pdf_link['href'])
        
        # 下载PDF文件
        pdf_response = requests.get(pdf_url, headers=HEADERS)
        pdf_response.raise_for_status()
        
        # 生成文件名
        filename = os.path.join(DOWNLOAD_DIR, pdf_url.split('/')[-1])
        
        # 保存文件
        with open(filename, 'wb') as f:
            f.write(pdf_response.content)
            
        print(f"成功下载: {filename}")
        
    except Exception as e:
        print(f"下载失败: {url} - {str(e)}")
    finally:
        time.sleep(REQUEST_DELAY)

if __name__ == "__main__":
    setup_download_dir()
    
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

    for idx, url in enumerate(sample_urls, 1):
        print(f"正在处理 [{idx}/{len(sample_urls)}]: {url}")
        download_pdf(url)

    print("所有下载任务完成！")
