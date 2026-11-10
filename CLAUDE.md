# 學測七千單字查詢

給台灣準備學測的高中生查單字的靜態網站，部署在 GitHub Pages：https://aaronhuang1006-debug.github.io/vocab-7000/
作者是英文家教黃咨翰。回覆一律用台灣繁體中文。

## 檔案
- `index.html`：整個網頁（搜尋、排版、發音），詞表與級別以 `RAW` 字串內嵌在 script 裡（每行 `headword|level|同形異義標記`，共 6,371 行）。
- `L1.txt`–`L6.txt`：各級單字內容，網頁依查詢的級別用 `fetch("L{n}.txt")` 載入並解析。
- `LP.txt`：591 個學測常考片語的內容（headword 行寫成 `phrase | P`，沒有字根行）。片語清單在 `tools/phrases_list.txt`，也以 `phrase|P|` 的形式加在 `index.html` 的 `RAW` 詞表後面；網頁把片語當成等級「P」處理，所以搜尋、單字本、字卡、單字表都通用。片語 headword 裡的 sb／sth／one's／oneself 只放在兩段固定字之間。
- `exams.json`：108–115 學測歷屆試題比對結果（每個詞條出現在哪一年、哪個大題、哪一句），由 tools/exam_index.py 從試卷 PDF 文字產生（`python3 exam_index.py <試卷txt資料夾> exams.json phrases_list.txt`，需要旁邊有 words.json）；比對時略過閱讀測驗題目固定句型；170 個功能詞（冠詞、代名詞、介系詞、連接詞、be／助動詞等）列在 `skip`，不列出歷屆試題。
- `sw.js`、`manifest.webmanifest`、`icon-*.png`、`apple-touch-icon.png`：讓網站可加入手機主畫面（PWA）並離線使用。
- 單字本存在學生瀏覽器的 localStorage（`vocab7000.book.v1`），沒有伺服器。不要改這個 key 或網站網址，否則學生的單字本會消失。
- 詞表來源是大考中心高中英文參考詞彙表的舊版（每級約 1,080 字）。不要換成 111 學年度新版。

## 內容格式（每個字一段，段與段之間空一行）
```
headword | L級別
詞性. 中文意思 | 常考搭配、句型或易錯點（可空，但 | 要保留）
例: 英文例句 | 中文翻譯
相關: 字(類型,中文) / 字(類型,中文)
字根: 部件(意思) + 部件(意思) | 說明 | 同字根字1, 同字根字2
```
- headword 必須與 `index.html` 內 `RAW` 詞表的寫法一字不差，否則網頁查不到。
- 詞性只能用 n. v. adj. adv. prep. conj. pron. aux. art. interj. num.；一字多義分行，最常用的在前。
- 相關字類型只能是：衍生字、同義字、反義字、易混淆字、片語、相關字；括號內用半形逗號。
- 字根只寫有可靠字源的；基礎字或不確定時整行省略，不可編造。
- 中文用台灣用語，不可出現簡體字或中國大陸用語。

## 工作流程
- 改動網頁或內容後，先用 `python3 -m http.server` 在本機開 http://localhost:8000 測試（直接雙擊 index.html 會因為無法 fetch 而查不到詞義）。
- **改了任何網站檔案（尤其 L?.txt、index.html）都要把 `sw.js` 的 `VERSION` 加 1**，否則已安裝到主畫面的學生會一直看到舊的快取內容。
- 咨翰確認後再 commit 並 push 到 main；GitHub Pages 約 1–2 分鐘後更新，學生端即生效。
- 學生正在使用這個網站：push 前要確認所有查詢仍正常，不要推上未經確認的改動。

## 已知可改進
- 字根行比例：L4 約 44%、L5 約 26%（偏少）、L6 約 56%。
- 少數例句跨字重複或長度偏長／偏短。
