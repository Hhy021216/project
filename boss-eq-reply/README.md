# BOSS 高情商回复助手

Chrome Manifest V3 浏览器扩展。在招聘平台会话页读取当前对话与简历项目经历，调用大模型生成**三条**可直接复制的高情商回复。

> **只辅助，不自动发送。** 所有回复需人工确认后手动复制，避免误发风险——这是本项目的核心设计原则。

## 功能

- 在 BOSS 直聘会话页面注入侧边面板，一键生成回复
- 结合简历中的项目经历作答，回复贴合候选人真实背景，不空泛
- 一次生成三条候选，风格各异，可自由选择复制
- 支持自定义模型服务商与 API Key（本地保存）

## 安装

1. 下载或克隆本目录
2. 打开 Chrome，访问 `chrome://extensions/`
3. 右上角开启「开发者模式」
4. 点击「加载已解压的扩展程序」，选择本目录
5. 打开扩展设置页，填入模型服务商与 API Key

要求 Chrome 120 及以上。

## 使用

1. 登录 BOSS 直聘，进入任意会话页面
2. 点击工具栏中的扩展图标，展开侧边面板
3. 在设置中完善个人简历项目经历（供生成时参考）
4. 点击生成，得到三条候选回复，选择满意的一条复制后手动发送

## 架构

```
manifest.json          MV3 声明：权限、内容脚本注入规则、CSP
├── loader.js          content script 入口，负责注入面板资源
├── panel.js / .css    侧边面板 UI 与交互
├── reader.js          从当前页面提取会话内容与简历信息
├── core.js            提示词编排、三条回复的生成逻辑
├── background.js      Service Worker，统一转发模型 API 请求（避开页面 CORS 限制）
├── options.html/js/css  设置界面
├── documents.js       帮助文档与说明内容
└── reference.json     提示词参考素材
```

### 分层思路

- **页面层**（`loader` / `panel` / `reader`）只负责读 DOM 与渲染，不直接调用外部 API
- **服务层**（`background.js`）作为唯一出网出口，统一处理鉴权与请求
- **逻辑层**（`core.js`）与 UI 解耦，便于替换模型或调整提示词策略

## 权限说明

| 权限 | 用途 |
|------|------|
| `storage` | 保存用户配置与 API Key（仅本地） |
| `clipboardWrite` | 一键复制生成的回复 |
| `host_permissions` | 仅授权目标招聘站点与模型 API 域名，白名单式限定 |

安全约束：

- `content_security_policy` 锁定 `script-src 'self'`，禁止任何远程脚本执行
- 不注入第三方统计或追踪脚本
- API Key 仅存于浏览器本地存储，不上传至任何第三方服务器

## 技术栈

- Chrome Extension Manifest V3（原生 JS，无构建依赖）
- Service Worker + Content Script 通信
- 后端模型：支持 DeepSeek 与 DashScope（Qwen）等 OpenAI 兼容接口

## 注意

- 本扩展仅辅助撰写回复，不对沟通结果作任何保证
- 使用前请自行确认目标平台的服务条款
- 请勿将填有真实 API Key 的配置文件提交到公开仓库
