**功能**
- 登入東華學生系統（你在瀏覽器輸入驗證碼）並抓取所有課程成績。
- 同時計算 4.0 與 4.3 制 GPA（到小數點第三位）。
- 統計總修學分數。
- 把結果存成試算表。

**需要準備**
- 已安裝 Google Chrome。
- 與你的 Chrome 版本相符的 ChromeDriver。
- Python 3.8 以上。

**安裝套件**
- 在這個資料夾開啟終端機（macOS）或命令提示字元（Windows）。
- 執行下面的命令下載依賴套件（怕污染）開發環境的話可以創建一個虛擬環境喔～
  - macOS/Linux：`python3 -m pip install -r requirements.txt`
  - Windows：`py -m pip install -r requirements.txt`

若出現找不到 pip，可改用：`python -m pip install -r requirements.txt`。

**設定 ChromeDriver 路徑**
- 程式預設 ChromeDriver 路徑為 `/usr/local/bin/chromedriver`。
- 如果你的路徑不同，請將路徑改成你的實際位置（例如 Windows 可用 `C:\\donwload\\chromedriver.exe`）。

如何取得 ChromeDriver：
- 前往官方網站下載與你 Chrome 相同版本的 ChromeDriver，解壓縮後記下放置位置。

**如何執行**
- 在終端機／命令提示字元輸入：`python gpa_report.py`（macOS/Linux 也可用 `python3 gpa_report.py`）
- 依指示輸入：
  - `學號`
  - `密碼`
- 會自動開啟瀏覽器，請在那裡輸入驗證碼並按「登入」。
- 回到終端機，依提示按下 Enter。
- 程式會等待頁面資料穩定後再讀取。請先不要關掉瀏覽器，直到終端機出現「抓到課程數：X」。

**你會看到什麼結果**
- 終端機會顯示：
  - 總 GPA (4.0)
  - 總 GPA (4.3)
  - 總修學分
  - 各等第的「門數」與「該等第學分數」（已作對齊，方便閱讀）
- 同資料夾會產生 `results.csv`，內容包含上述資訊與課程清單。

**小提醒與常見問題**
- 太早關閉瀏覽器可能導致資料不完整。
- 若 ChromeDriver 版本與 Chrome 不符，瀏覽器可能無法啟動。請更新 ChromeDriver 或在 `gpa_report.py` 中改成正確的路徑。

完成！照上述步驟執行後，打開 `results.csv` 即可查看整理好的 GPA 報表。
