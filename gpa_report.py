from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from typing import Dict, List, Tuple
import csv
import os
import getpass
import re


LOGIN_URL = 'https://sys.ndhu.edu.tw/CTE/Ed_StudP_WebSite/Login.aspx'


def create_chrome_driver(chromedriver_path: str, headless: bool = False):
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless")
    try:
        from selenium.webdriver.chrome.service import Service
        service = Service(chromedriver_path)
        return webdriver.Chrome(service=service, options=options)
    except Exception as e4:
        try:
            return webdriver.Chrome(executable_path=chromedriver_path, chrome_options=options)
        except Exception as e3:
            raise RuntimeError(
                "Failed to start Chrome WebDriver. "
                "Tried Selenium 4 and 3 styles. "
                f"Check chromedriver path/version match with Chrome. Errors: [{e4}] [{e3}]"
            )


def compute_gpa(names: List[str], credits: List[float], grades: List[str]) -> Tuple[float, float, float, Dict[str, int], Dict[str, float], list]:
    convert_40 = {
        'A+': 4.0, 'A': 4.0, 'A-': 3.67,
        'B+': 3.33, 'B': 3.0, 'B-': 2.67,
        'C+': 2.33, 'C': 2.0, 'C-': 1.67,
        'D': 1.33, 'E': 0.0
    }
    convert_43 = {
        'A+': 4.3, 'A': 4.0, 'A-': 3.7,
        'B+': 3.3, 'B': 3.0, 'B-': 2.7,
        'C+': 2.3, 'C': 2.0, 'C-': 1.7,
        'D': 1.3, 'E': 0.0
    }

    rows = []
    total_credit = 0.0
    total_gp_40 = 0.0
    total_gp_43 = 0.0
    grade_counts: Dict[str, int] = {grade: 0 for grade in convert_40}
    grade_credits: Dict[str, float] = {grade: 0.0 for grade in convert_40}

    for n, c, g in zip(names, credits, grades):
        if ('操行' in str(n)) or (float(c) <= 0):
            continue

        gg = str(g).strip().upper()
        if gg not in convert_40:
            if re.search(r'[甲乙丙丁優良可|()]+', gg):
                continue
            continue

        credit_val = float(c)
        gp_40 = convert_40[gg]
        gp_43 = convert_43[gg]

        total_credit += credit_val
        total_gp_40 += credit_val * gp_40
        total_gp_43 += credit_val * gp_43
        grade_counts[gg] += 1
        grade_credits[gg] += credit_val
        rows.append((str(n), credit_val, gg))

    overall_gpa_40 = round(total_gp_40 / total_credit, 3) if total_credit else 0.0
    overall_gpa_43 = round(total_gp_43 / total_credit, 3) if total_credit else 0.0
    return overall_gpa_40, overall_gpa_43, total_credit, grade_counts, grade_credits, rows


def fetch_scores_with_manual_captcha(std_id: str, std_pwd: str):
    # chromedriver 路徑請改成你自己的路徑
    driver = create_chrome_driver("/usr/local/bin/chromedriver", headless=False)

    wait = WebDriverWait(driver, 30)
    try:
        driver.get(LOGIN_URL)

        uid = wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_txtUID")))
        uid.clear()
        uid.send_keys(std_id)

        pwd = driver.find_element(By.ID, "ContentPlaceHolder1_txtPassword")
        pwd.clear()
        pwd.send_keys(std_pwd)

        print("請在『瀏覽器』輸入驗證碼並點【登入】。登入成功後，回到此視窗按 Enter 繼續…", flush=True)
        input()

        gpa_tab = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/form[2]/div[4]/div/ul/li[3]/a')))
        gpa_tab.click()

        wait.until(EC.number_of_windows_to_be(2))
        driver.switch_to.window(driver.window_handles[-1])

        wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_YearSemeDDList")))
        driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_YearSemeDDList"]/option[@value="0:0"]').click()

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        credits, grades, names = [], [], []
        for td in soup.find_all("td"):
            head = td.get('data-th')
            if head == "成績":
                grades.append(td.get_text(strip=True))
            elif head == "學分":
                text = td.get_text(strip=True)
                try:
                    credits.append(float(text))
                except ValueError:
                    credits.append(0.0)
            elif head == "科目名稱":
                names.append(td.get_text(strip=True))

        n = min(len(names), len(credits), len(grades))
        return names[:n], credits[:n], grades[:n]

    finally:
        try:
            driver.quit()
        except Exception:
            pass


def save_to_csv(filepath: str, overall_40: float, overall_43: float, total_credit: float, grade_counts: Dict[str, int], grade_credits: Dict[str, float], rows: list):
    os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['總 GPA (4.0)', f"{overall_40:.3f}"])
        writer.writerow(['總 GPA (4.3)', f"{overall_43:.3f}"])
        credit_text = f"{total_credit:.3f}".rstrip('0').rstrip('.')
        writer.writerow(['總修學分', credit_text])
        writer.writerow([])
        writer.writerow(['分數等第', '門數', '該等第學分數'])
        for grade, count in grade_counts.items():
            cred_text = f"{grade_credits.get(grade, 0.0):.3f}".rstrip('0').rstrip('.')
            writer.writerow([grade, count, cred_text])
        writer.writerow([])
        writer.writerow(['科目名稱', '學分', '成績'])
        writer.writerows(rows)


if __name__ == "__main__":
    sid = input('學號：').strip()
    spw = getpass.getpass('密碼：').strip()

    names, credits, grades = fetch_scores_with_manual_captcha(sid, spw)
    print(f'抓到課程數：{len(names)}')

    overall_40, overall_43, total_credit, grade_counts, grade_credits, rows = compute_gpa(names, credits, grades)
    print(f'總 GPA (4.0): {overall_40:.3f}')
    print(f'總 GPA (4.3): {overall_43:.3f}')
    credit_text = f"{total_credit:.3f}".rstrip('0').rstrip('.')
    print(f'總修學分：{credit_text}')
    print('各等第門數與學分數：')
    for grade, count in grade_counts.items():
        cred_text = f"{grade_credits.get(grade, 0.0):.3f}".rstrip('0').rstrip('.')
        label = f"{grade} " if grade in {"A", "B", "C", "D", "E"} else grade
        count_text = f"{count} " if 0 <= count < 10 else f"{count}"
        print(f'  {label}: 門數 {count_text}, 學分 {cred_text}')

    out_path = 'results.csv'
    save_to_csv(out_path, overall_40, overall_43, total_credit, grade_counts, grade_credits, rows)
    print(f'已輸出 CSV:{out_path}')
