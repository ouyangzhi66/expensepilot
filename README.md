# ExpensePilot 路 璐㈠姟鎶ラ攢 Agent

[Gitee 浠撳簱](https://gitee.com/ouyangzhi66/expensepilot) 路 [Issues](https://gitee.com/ouyangzhi66/expensepilot/issues) 路 [璇勬祴鎶ュ憡](docs/eval.md) 路 [寮€鍙戞棩蹇梋(docs/log.md)

> 鍛樺伐涓€鍙ヨ瘽鎻忚堪鍑哄樊 / 鎷涘緟璐圭敤锛孉gent 鏌ュ埗搴︺€佺畻棰濆害銆侀獙鍙戠エ銆佺敓鎴愬嚟璇佽崏绋匡紱瓒呰鍒欒嚜鍔ㄨ浆浜哄伐銆?
[Demo](TODO) 路 [3 鍒嗛挓瑙嗛](TODO)

## 涓轰粈涔堜笉鏄張涓€涓?RAG 鑱婂ぉ妗?
鎶ラ攢鏄竴涓姝ヤ换鍔★細鏌ュ埗搴?鈫?鏌ラ搴?鈫?鏍￠獙鍙戠エ 鈫?鐢熸垚鍑瘉 鈫?浜哄伐纭銆傚崟杞?RAG 鍙兘鍥炵瓟鈥滀綇瀹夸笂闄愬灏戔€濓紝涓嶈兘瀹屾垚浠诲姟銆傝繖涓」鐩璇佹槑鐨勬槸锛?
- 澶氬伐鍏风紪鎺掞紙7 涓伐鍏凤級
- 澶氳疆妲戒綅濉厖涓庤拷闂?- 鏉′欢鍒嗘敮涓庝汉鍦ㄥ洖璺紙瓒呴檺 / 瓒婃潈杞汉宸ワ級
- 鍙瘎娴嬶紙30 鏉″満鏅?+ 鎸囨爣锛?- 鍙娴嬶紙瀹¤鏃ュ織 / trace锛?
## 鏋舵瀯

```text
鍛樺伐
  鈹?  鈻?Streamlit UI 鈹€鈹€鈻?LangGraph 鈹€鈹€鈻?policy_search 鈹€鈹€鈻?Postgres + pgvector
                    鈹?                    鈹溾攢鈹€鈻?budget_check 鈹€鈹€鈻?Postgres
                    鈹溾攢鈹€鈻?voucher_create 鈹€鈹€鈻?Postgres
                    鈹斺攢鈹€鈻?ask_human 鈹€鈹€鈻?寰呭姙 / 瀹¤鏃ュ織
```

## 蹇€熷紑濮?
### 0. 鍏嬮殕

```powershell
git clone https://gitee.com/ouyangzhi66/expensepilot.git
cd expensepilot
```

### 1. 瀹夎 Python 3.11
瀹夎鏃跺嬀閫?`Add python.exe to PATH`銆?
### 2. 瑁呬緷璧?
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt -r requirements-dev.txt
Copy-Item .env.example .env
```

### 3. 鏁版嵁搴擄紙浜岄€変竴锛?
- **A. Supabase锛堟帹鑽愶紝鍏?Docker锛?*锛氭柊寤洪」鐩?鈫?SQL Editor 鎵ц `create extension if not exists vector;` 鈫?鎶?Session Pooler 杩炴帴涓插～鍒?`.env` 鐨?`DATABASE_URL`銆?- **B. 鏈湴 Docker**锛歚docker compose up -d db`銆?
楠岃瘉杩炴帴锛?
```powershell
python scripts/db_check.py
```

鐪嬪埌 PostgreSQL 鐗堟湰鍜?`pgvector: True` 鍗虫垚鍔熴€?
### 4. 鑷

```powershell
.\scripts\check.ps1
```

### 5. 鍒嗘敮涓庤繙绋?
- 涓诲垎鏀細`master`锛圙itee 榛樿锛?- 杩滅▼锛歚origin` 鈫?`https://gitee.com/ouyangzhi66/expensepilot.git`

> Gitee 涓嶈窇 GitHub Actions銆俙.github/workflows/ci.yml` 鍙湪浠ュ悗闀滃儚鍒?GitHub 鏃剁敤锛涙棩甯哥敤 `scripts/check.ps1`锛孏itee Go 鍙€夛紝涓嶅奖鍝嶄氦浠樸€?

## 璇勬祴

| 鎸囨爣 | 鐩爣 | 褰撳墠 |
|---|---|---|
| 浠诲姟瀹屾垚鐜?| 鈮?5% | TODO |
| 鍑瘉瀛楁瀹屾暣鐜?| 鈮?5% | TODO |
| 瓒呴檺 / 瓒婃潈鎷︽埅鐜?| 100% | TODO |
| RAG 寮曠敤鍛戒腑鐜?| 鈮?0% | TODO |
| P95 鏃跺欢 | 鈮?s | TODO |

鍦烘櫙鍒嗗竷涓庣敤渚嬭 [docs/eval.md](docs/eval.md)銆乕eval/cases.csv](eval/cases.csv)銆?
## Roadmap

### MVP锛?0 澶╋級

- [ ] D01 鏁版嵁琛?/ 鍚堟垚鏁版嵁 / 10 鏉¤瘎娴嬮泦
- [ ] D02 鍒跺害 RAG锛氬垏鍒嗐€乪mbedding銆乸gvector銆佸紩鐢?- [ ] D03 LangGraph 楠ㄦ灦 + `policy_search`
- [ ] D04 `budget_check` + seed SQL
- [ ] D05 `voucher_create` + JSON Schema
- [ ] D06 澶氳疆妲戒綅 + 缂轰俊鎭拷闂?- [ ] D07 Streamlit happy path
- [ ] D08 浜哄湪鍥炶矾 + 瀹¤鏃ュ織
- [ ] D09 15 鏉¤瘎娴?+ top-3 淇
- [ ] D10 閮ㄧ讲 / README / 3 鍒嗛挓瑙嗛

### 鍔犲浐锛圖11-D21锛?
- [ ] 鍙戠エ OCR + 绁ㄩ潰鏍￠獙
- [ ] 30 鏉¤瘎娴?+ 閿欒鍒嗙被
- [ ] Langfuse trace / 鎴愭湰缁熻
- [ ] Vue 3 鍓嶇锛堝彲閫夛級
- [ ] 1 椤甸」鐩姤鍛婏紙Gitee Pages 鎴?`docs/report.md`锛?- [ ] Dockerfile / compose 涓€閿捣锛堥潰璇曡瀹瑰櫒鍖栵級

## 姣忔棩 Gitee 娴佺▼

1. 寮€宸ワ細鎶婂綋澶?issue 绉诲埌 Doing锛屽啓涓€鍙モ€滀粖鏃ョ洰鏍団€濄€?2. 寮€鍙戯細姣?30-45 鍒嗛挓 commit 涓€娆★紝Conventional Commits銆?3. 鏀跺伐锛氭洿鏂?`docs/log.md`锛屽叧闂?issue锛孯EADME 杩涘害鎵撳嬀銆?4. 姣忓ぉ push 鍒?`master`锛涙瘡鍛ㄦ棩鎵?tag锛坄v0.1.0`锛夛紝鍐?Release notes銆?
> 璐＄尞搴︾粺璁¤姹?`git config user.email` 涓?Gitee 缁戝畾閭涓€鑷淬€傚綋鍓嶆湰鏈烘槸 `1161655868@qq.com`锛屽幓 Gitee銆岃缃?鈫?閭绠＄悊銆嶇‘璁ゅ凡缁戝畾锛屽惁鍒欐彁浜や笉浼氬彉缁裤€?
## 浠撳簱缁撴瀯

```text
expensepilot/
鈹溾攢 src/expensepilot/      # Agent / tools / api
鈹溾攢 eval/                  # 娴嬭瘯闆嗕笌璇勬祴鑴氭湰
鈹溾攢 docs/                  # 鏃ュ織銆佽瘎娴嬨€丄DR
鈹溾攢 scripts/               # check.ps1 鏈湴鑷
鈹溾攢 tests/                 # pytest
鈹溾攢 .github/               # GitHub 闀滃儚鐢?CI + issue 妯℃澘
鈹斺攢 docker-compose.yml     # Postgres + pgvector锛堝彲閫夛級
```

## License

MIT

