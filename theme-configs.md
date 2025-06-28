# 🎨 agnflow 主题配置指南

agnflow 文档支持多种美观的主题配置，您可以根据需要选择不同的主题风格。

## 🌈 推荐主题配置

### 1. 🚀 现代科技主题 (当前使用)

```yaml
theme:
  name: material
  palette:
    # 现代渐变主题 - 蓝紫渐变
    - media: "(prefers-color-scheme: light)"
      scheme: default
      primary: deep purple
      accent: deep purple
    # 深色主题 - 科技感
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      primary: deep purple
      accent: deep purple
```

**特点**: 现代感强，蓝紫渐变，科技感十足

### 2. 🌊 海洋主题

```yaml
theme:
  name: material
  palette:
    - media: "(prefers-color-scheme: light)"
      scheme: default
      primary: blue
      accent: teal
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      primary: blue
      accent: teal
```

**特点**: 清新海洋蓝，适合技术文档

### 3. 🌿 自然主题

```yaml
theme:
  name: material
  palette:
    - media: "(prefers-color-scheme: light)"
      scheme: default
      primary: green
      accent: light green
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      primary: green
      accent: light green
```

**特点**: 自然绿色，舒适护眼

### 4. 🔥 火焰主题

```yaml
theme:
  name: material
  palette:
    - media: "(prefers-color-scheme: light)"
      scheme: default
      primary: red
      accent: orange
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      primary: red
      accent: orange
```

**特点**: 热情红色，充满活力

### 5. 💎 宝石主题

```yaml
theme:
  name: material
  palette:
    - media: "(prefers-color-scheme: light)"
      scheme: default
      primary: indigo
      accent: pink
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      primary: indigo
      accent: pink
```

**特点**: 高贵紫粉，优雅大方

### 6. 🌅 日落主题

```yaml
theme:
  name: material
  palette:
    - media: "(prefers-color-scheme: light)"
      scheme: default
      primary: orange
      accent: amber
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      primary: orange
      accent: amber
```

**特点**: 温暖橙黄，温馨舒适

## 🎯 高级主题配置

### 完整功能配置

```yaml
theme:
  name: material
  language: en  # 或 zh
  features:
    # 导航功能
    - navigation.tabs
    - navigation.sections
    - navigation.expand
    - navigation.top
    - navigation.footer
    - navigation.instant
    - navigation.instant.prefetch
    - navigation.instant.loading
    - navigation.prune
    - navigation.tracking
    
    # 内容功能
    - content.code.copy
    - content.code.annotate
    - content.code.select
    - content.tabs.link
    - content.tooltips
    - content.action.edit
    - content.action.view
    
    # 搜索功能
    - search.suggest
    - search.highlight
    - search.share
    
    # 其他功能
    - header.autohide
    - toc.follow
    - toc.integrate
    - announce.dismiss
  
  # 字体配置
  font:
    text: Roboto
    code: Roboto Mono
  
  # 图标配置
  icon:
    repo: fontawesome/brands/github
    edit: material/pencil
    view: material/eye
    previous: material/arrow-left
    next: material/arrow-right
    search: material/magnify
    close: material/close
    menu: material/menu
    language: material/translate
    share: material/share-variant
    download: material/download
    fullscreen: material/fullscreen
    fullscreen_exit: material/fullscreen-exit
    top: material/arrow-up
    home: material/home
```

## 🎨 自定义主题

### 创建自定义主题

1. **选择基础颜色**
   ```yaml
   primary: [颜色名称]  # 主色调
   accent: [颜色名称]   # 强调色
   ```

2. **可用颜色选项**
   - `red`, `pink`, `purple`, `deep purple`
   - `indigo`, `blue`, `light blue`, `cyan`
   - `teal`, `green`, `light green`, `lime`
   - `yellow`, `amber`, `orange`, `deep orange`
   - `brown`, `grey`, `blue grey`

3. **主题模式**
   - `default`: 浅色主题
   - `slate`: 深色主题

## 🔧 应用主题

### 方法一：修改配置文件

编辑 `mkdocs.yml` 或 `mkdocs-en.yml` 文件中的 `theme.palette` 部分。

### 方法二：创建主题变体

```bash
# 创建主题变体配置文件
cp mkdocs.yml mkdocs-ocean.yml
cp mkdocs-en.yml mkdocs-en-ocean.yml

# 修改主题配置
# 然后使用不同的配置文件构建
mkdocs build -f mkdocs-ocean.yml -d site/zh-ocean
mkdocs build -f mkdocs-en-ocean.yml -d site/en-ocean
```

## 📱 响应式设计

所有主题都支持响应式设计，在不同设备上都有良好的显示效果：

- **桌面端**: 完整功能，侧边导航
- **平板端**: 自适应布局，触摸友好
- **手机端**: 移动优化，手势支持

## 🌙 深色模式

所有主题都支持自动深色模式切换：

- 根据系统设置自动切换
- 手动切换按钮
- 平滑过渡动画

## 🎯 推荐组合

### 技术文档推荐
- **主色调**: `deep purple` 或 `blue`
- **强调色**: `deep purple` 或 `teal`
- **深色模式**: `slate`

### 创意项目推荐
- **主色调**: `pink` 或 `orange`
- **强调色**: `purple` 或 `amber`
- **深色模式**: `slate`

### 企业文档推荐
- **主色调**: `blue` 或 `indigo`
- **强调色**: `blue` 或 `teal`
- **深色模式**: `slate`

## 🚀 性能优化

- 使用 Material Design 图标
- 优化字体加载
- 压缩 CSS 和 JS
- 图片懒加载
- 代码高亮优化

选择适合您项目的主题，让文档更加吸引人！ 