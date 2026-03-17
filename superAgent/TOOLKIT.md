# superAgent 工具清单

本文档列出了 superAgent 所有可用工具的详细说明。

---

## 📁 文件系统工具 (filesystem.py)

### read_file

**描述**：读取文件内容

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| path | string | ✅ | 文件路径（相对于工作空间） |

**示例**：
```
read_file(path="config.json")
```

---

### write_file

**描述**：写入内容到文件（创建或覆盖）

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| path | string | ✅ | 文件路径（相对于工作空间） |
| content | string | ✅ | 要写入的内容 |

**示例**：
```
write_file(path="test.txt", content="Hello World")
```

---

### list_dir

**描述**：列出目录下的文件和子目录

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| path | string | ❌ | 目录路径（默认为当前目录 "."） |

**示例**：
```
list_dir(path="agent/tools")
```

---

### edit_file

**描述**：替换文件中的特定字符串

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| path | string | ✅ | 文件路径 |
| old_string | string | ✅ | 要替换的原始字符串 |
| new_string | string | ✅ | 替换后的新字符串 |

**示例**：
```
edit_file(path="config.json", old_string='"enabled": false', new_string='"enabled": true')
```

---

### shell

**描述**：在工作空间目录中执行 shell 命令

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| command | string | ✅ | 要执行的 shell 命令 |

**示例**：
```
shell(command="git status")
```

**注意**：命令超时时间为 30 秒

---

## 🧠 记忆工具 (memory_tools.py)

### save_memory

**描述**：保存笔记到长期记忆（MEMORY.md）

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| note | string | ✅ | 要保存的笔记内容 |

**示例**：
```
save_memory(note="用户偏好使用中文交流")
```

---

### read_memory

**描述**：读取完整的长期记忆内容

**参数**：无

**示例**：
```
read_memory()
```

---

### save_today_note

**描述**：保存笔记到今日日志

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| note | string | ✅ | 要保存的笔记内容 |

**示例**：
```
save_today_note(note="完成了配置文件修改")
```

---

## 🤖 子代理工具 (subagent_tools.py)

### spawn_agent

**描述**：生成后台子代理异步处理长时间任务，返回 task_id

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| prompt | string | ✅ | 给子代理的任务描述 |
| session_id | string | ❌ | 可选的会话 ID |

**示例**：
```
spawn_agent(prompt="分析 logs 目录下所有日志文件并生成报告")
```

---

### get_agent_result

**描述**：通过 task_id 获取后台子代理任务的执行结果

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| task_id | string | ✅ | spawn_agent 返回的任务 ID |

**示例**：
```
get_agent_result(task_id="task_123")
```

**返回**：任务状态、结果、错误信息

---

## 📸 截图工具 (screenshot.py)

### screenshot

**描述**：截取当前屏幕画面并保存到文件

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| filename | string | ❌ | 截图文件名（默认：screenshot_YYYYMMDD_HHMMSS.png） |

**示例**：
```
screenshot(filename="desktop.png")
```

**保存位置**：`.superagent/screenshots/`

**依赖**：需要安装 Pillow（`pip install Pillow`）

---

## 🌐 网络工具 (web.py)

### web_search

**描述**：搜索互联网信息（使用 DuckDuckGo，无需 API Key）

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| query | string | ✅ | 搜索关键词 |
| max_results | integer | ❌ | 最大结果数（默认：5） |

**示例**：
```
web_search(query="Python 最新版本", max_results=10)
```

**依赖**：需要安装 requests（`pip install requests`）

---

### web_fetch

**描述**：获取并提取网页文本内容

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| url | string | ✅ | 要获取的网页 URL |
| max_length | integer | ❌ | 最大内容长度（默认：5000） |

**示例**：
```
web_fetch(url="https://www.python.org", max_length=10000)
```

---

### web_request

**描述**：发送 HTTP 请求到任意 URL（适用于 API 调用）

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| url | string | ✅ | 请求的 URL |
| method | string | ❌ | HTTP 方法：GET/POST/PUT/DELETE（默认：GET） |
| headers | object | ❌ | HTTP 请求头（JSON 对象） |
| body | string | ❌ | 请求体（用于 POST/PUT） |

**示例**：
```
web_request(
  url="https://api.example.com/data",
  method="POST",
  headers={"Content-Type": "application/json"},
  body='{"key": "value"}'
)
```

**返回**：状态码、响应头、响应体

---

## 🌐 网络工具 - 基础版 (web_tools.py)

### http_get

**描述**：发送 HTTP GET 请求获取网页内容

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| url | string | ✅ | 要访问的 URL |
| timeout | integer | ❌ | 超时时间（秒），默认 10 |

**示例**：
```
http_get(url="https://example.com", timeout=15)
```

**特点**：使用 Python 标准库 urllib，无需额外依赖

---

### http_post

**描述**：发送 HTTP POST 请求

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| url | string | ✅ | 要访问的 URL |
| data | string | ✅ | POST 数据（JSON 格式） |
| timeout | integer | ❌ | 超时时间（秒），默认 10 |

**示例**：
```
http_post(url="https://api.example.com", data='{"name": "test"}')
```

---

## 📊 工具统计

| 类别 | 工具数量 |
|------|----------|
| 文件系统 | 5 |
| 记忆管理 | 3 |
| 子代理 | 2 |
| 截图 | 1 |
| 网络 | 5 |
| **总计** | **16** |

---

## 🔧 依赖说明

| 工具 | 依赖 | 安装命令 |
|------|------|----------|
| screenshot | Pillow | `pip install Pillow` |
| web_search / web_fetch / web_request | requests | `pip install requests` |
| http_get / http_post | 无（标准库） | - |

---

*文档生成时间：2026-03-15*