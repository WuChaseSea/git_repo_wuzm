# 武汉浪漫之旅 - 国庆情侣旅行攻略

一个现代化的旅游攻略网页应用，专为国庆期间武汉四天三夜情侣旅行设计。

## 功能特性

1. **行程规划**
   - 根据国庆假期时间安排最优游览路线
   - 时间安排、景点推荐、美食攻略
   - 结合实时天气数据调整行程建议
   - 每日行程独立卡片展示，支持点击切换浏览
   - 景点信息以精美卡片形式呈现

2. **交互式地图展示**
   - 集成高德地图API
   - 展示武汉主要景点位置
   - 点击标记查看景点详情

3. **天气数据展示**
   - 响应式卡片式界面设计
   - 现代美学风格，界面色彩丰富
   - 实时天气信息和未来几天预报
   - 旅行建议基于天气情况

## 技术栈

- React.js
- 高德地图API
- CSS3 (渐变、动画效果)
- Responsive Design (响应式设计)

## 安装与运行

1. 克隆项目:
   ```
   git clone <repository-url>
   ```

2. 进入项目目录:
   ```
   cd wuhan-travel-app
   ```

3. 安装依赖:
   ```
   npm install
   ```

4. 运行开发服务器:
   ```
   npm start
   ```

5. 在浏览器中打开 `http://localhost:3000` 查看应用

## 项目结构

```
wuhan-travel-app/
├── public/
├── src/
│   ├── components/
│   │   ├── DayCard.js
│   │   ├── Navigation.js
│   │   └── Footer.js
│   ├── pages/
│   │   ├── ItineraryPage.js
│   │   ├── MapPage.js
│   │   └── WeatherPage.js
│   ├── App.js
│   ├── App.css
│   └── index.js
└── package.json
```

## 注意事项

1. 需要申请高德地图API密钥并替换 `MapPage.js` 中的 `YOUR_AMAP_KEY_HERE`
2. 天气数据目前为模拟数据，实际应用中需要接入天气API

## 许可证

MIT