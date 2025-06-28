#!/bin/bash

# agnflow 多语言文档构建脚本

echo "🚀 开始构建 agnflow 多语言文档..."

# 检查是否安装了 mkdocs
if ! command -v mkdocs &> /dev/null; then
    echo "❌ mkdocs 未安装，请先安装 mkdocs"
    echo "pip install mkdocs-material"
    exit 1
fi

# 创建构建目录
mkdir -p site

# 构建中文文档
echo "📖 构建中文文档..."
mkdocs build -f mkdocs.yml -d site/zh

# 构建英文文档
echo "📖 构建英文文档..."
mkdocs build -f mkdocs-en.yml -d site/en

# 创建语言切换页面
echo "🌐 创建语言切换页面..."

# 创建根目录的 index.html - 默认重定向到英文版
cat > site/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>agnflow - Multi-language Documentation</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 2rem;
            line-height: 1.6;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: white;
            padding: 3rem;
            border-radius: 16px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.15);
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        .container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #667eea, #764ba2, #667eea);
        }
        h1 {
            color: #333;
            margin-bottom: 1rem;
            font-size: 3rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .subtitle {
            color: #666;
            margin-bottom: 2rem;
            font-size: 1.2rem;
            font-weight: 300;
        }
        .description {
            color: #888;
            margin-bottom: 3rem;
            font-size: 1rem;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        }
        .language-links {
            display: flex;
            gap: 1.5rem;
            justify-content: center;
            flex-wrap: wrap;
            margin-bottom: 2rem;
        }
        .language-link {
            display: inline-block;
            padding: 1.2rem 2.5rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 12px;
            font-weight: 600;
            font-size: 1.1rem;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        .language-link::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }
        .language-link:hover::before {
            left: 100%;
        }
        .language-link:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.3);
        }
        .language-link.primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .github-link {
            margin-top: 2rem;
            padding: 0.5rem 1rem;
            background: #333;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-size: 0.9rem;
        }
        .github-link:hover {
            background: #555;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 agnflow</h1>
        <p>一个简洁的 Python 智能体工作流引擎</p>
        <p>A concise Python agent workflow engine</p>
        
        <div class="language-links">
            <a href="zh/" class="language-link">📖 中文文档</a>
            <a href="en/" class="language-link">📖 English Docs</a>
        </div>
        
        <a href="https://github.com/jianduo1/agnflow" class="github-link" target="_blank">
            🔗 GitHub Repository
        </a>
    </div>
</body>
</html>
EOF

echo "✅ 文档构建完成！"
echo "📁 构建结果位于 site/ 目录"
echo "🌐 中文文档: site/zh/"
echo "🌐 英文文档: site/en/"
echo "🏠 主页: site/index.html"

# 启动本地服务器（可选）
if [ "$1" = "--serve" ]; then
    echo "🌐 启动本地服务器..."
    echo "访问 http://localhost:8000 查看文档"
    python3 -m http.server 8000 --directory site
fi 