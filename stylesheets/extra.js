// 背景主题切换功能
(function() {
  'use strict';

  // 背景主题列表
  const backgrounds = [
    { name: 'default', label: '默认' },
    { name: 'starry', label: '星空' },
    { name: 'aurora', label: '极光' },
    { name: 'wave', label: '波浪' },
    { name: 'glow', label: '光晕' },
    { name: 'multicolor', label: '多色' },
    { name: 'deep', label: '深邃' }
  ];

  let currentBackgroundIndex = 0;

  // 创建背景切换按钮
  function createBackgroundToggle() {
    const button = document.createElement('button');
    button.className = 'background-toggle';
    button.innerHTML = '🎨';
    button.title = '切换背景主题';
    
    // 添加到页面
    document.body.appendChild(button);
    
    // 点击事件
    button.addEventListener('click', function() {
      currentBackgroundIndex = (currentBackgroundIndex + 1) % backgrounds.length;
      applyBackground(backgrounds[currentBackgroundIndex].name);
      updateButtonTitle();
      
      // 保存到本地存储
      localStorage.setItem('agnflow-background', backgrounds[currentBackgroundIndex].name);
    });
    
    return button;
  }

  // 应用背景主题
  function applyBackground(themeName) {
    const body = document.body;
    
    // 移除所有背景类
    backgrounds.forEach(bg => {
      body.classList.remove(`theme-${bg.name}`);
    });
    
    // 添加当前背景类
    if (themeName !== 'default') {
      body.classList.add(`theme-${themeName}`);
    }
  }

  // 更新按钮标题
  function updateButtonTitle() {
    const button = document.querySelector('.background-toggle');
    if (button) {
      const currentBg = backgrounds[currentBackgroundIndex];
      button.title = `当前: ${currentBg.label} | 点击切换`;
    }
  }

  // 初始化
  function init() {
    // 创建背景切换按钮
    const button = createBackgroundToggle();
    
    // 从本地存储恢复背景设置
    const savedBackground = localStorage.getItem('agnflow-background');
    if (savedBackground) {
      const index = backgrounds.findIndex(bg => bg.name === savedBackground);
      if (index !== -1) {
        currentBackgroundIndex = index;
        applyBackground(savedBackground);
      }
    }
    
    // 更新按钮标题
    updateButtonTitle();
    
    // 等待页面加载完成后确保按钮可见
    setTimeout(() => {
      if (button) {
        button.style.display = 'flex';
      }
    }, 1000);
  }

  // 页面加载完成后初始化
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})(); 