# 部署到 Streamlit Community Cloud

前置条件：GitHub 账号、Streamlit Cloud 账号（用 GitHub 登录）、Supabase 连接串、LLM API key。

## 1. 把 Gitee 仓库导入 GitHub

1. 打开 https://github.com/new/import 。
2. 填入 Gitee 仓库地址：`https://gitee.com/ouyangzhi66/expensepilot`。
3. 仓库名填 `expensepilot`，选 **Public**。
4. 点 **Begin import**，等 1-2 分钟。

如果导入失败，也可以新建空仓库后手动推：

```powershell
cd "D:\deeekseek工作区\expensepilot"
git remote add github https://github.com/<你的用户名>/expensepilot.git
git push github master
```

## 2. 在 Streamlit Cloud 新建应用

1. 打开 https://share.streamlit.io ，用 GitHub 登录。
2. 点 **New app**。
3. Repository 选 `<你的用户名>/expensepilot`，Branch 选 `master`，Main file 填 `app.py`。
4. 打开 **Advanced settings**，Python 版本选 **3.11**。
5. 点 **Deploy**。

第一次构建会安装 `requirements.txt`，包括 fastembed / onnxruntime，约 3-5 分钟。

## 3. 配置 Secrets

部署完成后进入应用 **Settings → Secrets**，粘贴：

```toml
DATABASE_URL = "postgresql://postgres.xxxx:密码@aws-0-ap-northeast-2.pooler.supabase.com:5432/postgres"
OPENAI_API_KEY = "sk-你的key"
OPENAI_BASE_URL = "https://api.deepseek.com/v1"
MODEL_NAME = "deepseek-chat"
EMBEDDING_MODEL = "BAAI/bge-small-zh-v1.5"
EMBEDDING_DIM = "512"
HF_ENDPOINT = "https://hf-mirror.com"
```

保存后点 **Reboot app**。

Secrets 只存在 Streamlit Cloud，不会进入 Git 仓库。

## 4. 验证

打开应用，依次试：

1. `住宿标准是多少` → 应引用 POL-001，回答 500/350；
2. `帮我报销` → 应追问 6 个槽位；
3. `李四，上海，2026-10-12到2026-10-13，住宿5000` → 应转人工并给工单号。

## 常见问题

| 现象 | 处理 |
|---|---|
| `ModuleNotFoundError` | 确认 `requirements.txt` 已提交，Reboot |
| `libgomp.so.1` 缺失 | 确认 `packages.txt` 里有 `libgomp1`，Reboot |
| 数据库连接超时 | 用 Session Pooler（IPv4），确认 Supabase 项目没暂停 |
| 首次回答很慢 | 在下载 embedding 模型（约 100MB），等一次即可 |
| 应用休眠 | Streamlit Cloud 免费版会休眠，打开后等唤醒 |

## 后续同步

Gitee 是主仓库，GitHub 是部署镜像。每次 push Gitee 后：

```powershell
git push github master
```

Streamlit Cloud 会自动重新部署。
