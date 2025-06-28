# 📚 agnflow 文档

agnflow 项目支持中英文双语文档，**默认显示英文版**。

## 🌐 多语言文档结构

```
docs/
├── zh/                    # 中文文档
│   ├── index.md          # 首页
│   ├── getting-started.md # 快速开始
│   ├── core-concepts.md   # 核心概念
│   ├── examples.md        # 示例
│   └── api-reference.md   # API 参考
├── en/                    # 英文文档 (默认)
│   ├── index.md          # Home
│   ├── getting-started.md # Getting Started
│   ├── core-concepts.md   # Core Concepts
│   ├── examples.md        # Examples
│   └── api-reference.md   # API Reference
└── README.md             # 本文档
```

## 🚀 构建文档

### 方法一：使用构建脚本（推荐）

```bash
# 构建所有语言版本的文档
./build_docs.sh

# 构建并启动本地服务器
./build_docs.sh --serve
```

**默认语言**: 英文版 (`site/en/`)

### 方法二：分别构建

```bash
# 构建中文文档
mkdocs build -f mkdocs.yml -d site/zh

# 构建英文文档 (默认)
mkdocs build -f mkdocs-en.yml -d site/en
```

### 方法三：本地预览

```bash
# 预览中文文档
mkdocs serve -f mkdocs.yml

# 预览英文文档 (默认)
mkdocs serve -f mkdocs-en.yml
```

## 📁 配置文件说明

### mkdocs.yml（中文版本）
- 语言设置：`language: zh`
- 导航指向：`zh/` 目录下的文档
- 主题切换：中文界面

### mkdocs-en.yml（英文版本 - 默认）
- 语言设置：`language: en`
- 导航指向：`en/` 目录下的文档
- 主题切换：英文界面

## 🎨 主题配置

### 当前主题特色
- **现代科技感**: 蓝紫渐变配色
- **响应式设计**: 支持桌面、平板、手机
- **深色模式**: 自动切换，护眼舒适
- **丰富功能**: 搜索、导航、代码高亮等

### 主题选择
查看 `theme-configs.md` 了解多种主题配置选项：
- 🚀 现代科技主题 (当前)
- 🌊 海洋主题
- 🌿 自然主题
- 🔥 火焰主题
- 💎 宝石主题
- 🌅 日落主题

## 🔧 添加新文档

### 1. 创建中文文档
在 `docs/zh/` 目录下创建新的 `.md` 文件，然后在 `mkdocs.yml` 的 `nav` 部分添加导航。

### 2. 创建英文文档
在 `docs/en/` 目录下创建对应的英文版本，然后在 `mkdocs-en.yml` 的 `nav` 部分添加导航。

### 3. 保持同步
确保中英文文档内容保持同步，包括：
- 文档结构
- 代码示例
- 图片资源
- 链接引用

## 🎨 文档规范

### 文件命名
- 使用小写字母和连字符
- 例如：`getting-started.md`、`api-reference.md`

### 标题格式
- 中文文档：使用中文标题
- 英文文档：使用英文标题
- 保持标题层级一致

### 代码示例
- 保持中英文代码示例一致
- 注释可以使用对应语言

### 图片和资源
- 图片路径使用相对路径
- 确保中英文文档都能正确访问

## 🌍 部署

构建完成后，`site/` 目录包含：
- `site/index.html` - 语言选择页面 (默认推荐英文)
- `site/zh/` - 中文文档
- `site/en/` - 英文文档 (默认)

可以部署到任何静态网站托管服务，如：
- GitHub Pages
- Netlify
- Vercel
- 阿里云 OSS
- 腾讯云 COS

## 🔄 更新流程

1. 修改中文文档（`docs/zh/`）
2. 同步更新英文文档（`docs/en/`）
3. 运行构建脚本：`./build_docs.sh`
4. 测试本地预览
5. 部署到生产环境

## 🌐 语言切换

### 自动语言检测
- 根据浏览器语言设置自动推荐
- 支持手动语言切换
- 记住用户语言偏好

### 默认语言设置
- **主页**: 英文版优先显示
- **自动重定向**: 根据用户语言偏好
- **语言选择**: 清晰的语言切换按钮

## 📝 注意事项

- 确保所有文档都有对应的中英文版本
- 保持文档结构的一致性
- 定期检查链接的有效性
- 更新时注意版本号的同步
- **英文版为默认语言，优先维护英文文档质量** 