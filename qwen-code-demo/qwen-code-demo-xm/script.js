// script.js
import { gaodeAPI } from './gaode-api.js';

// 情绪关键词映射
const moodKeywords = {
  // 负面情绪
  negative: [
    { keywords: ['累', '疲惫', '疲劳', '辛苦', '劳累'], response: '抱抱你~ 今天一定很辛苦吧。累了就休息一下，你值得被温柔对待。' },
    { keywords: ['难过', '伤心', '沮丧', '低落', '郁闷', '心情不好'], response: '难过的时候，允许自己脆弱一会儿。阴天之后总会放晴的，我会一直在这里陪着你。' },
    { keywords: ['焦虑', '烦躁', '不安', '紧张'], response: '深呼吸一下~ 把烦心事暂时放在一边，你已经做得很好了。' },
    { keywords: ['孤独', '寂寞'], response: '即使一个人，也不代表全世界都抛弃了你。你还有我，还有明天的太阳。' },
    { keywords: ['压力', '压抑'], response: '压力大的时候，就像背负了太多行李。不妨先放下一些，轻装上阵会更轻松哦。' }
  ],
  // 积极情绪
  positive: [
    { keywords: ['开心', '高兴', '快乐', '愉快', '兴奋'], response: '看到你开心，我也忍不住嘴角上扬了呢！愿你的每一天都像今天一样美好~' },
    { keywords: ['庆祝', '成功', '成就'], response: '为你鼓掌！🎉 值得庆祝的时刻就要尽情享受，你值得所有美好！' },
    { keywords: ['犒劳', '奖励'], response: '懂得犒劳自己的人，生活一定会回馈你更多的温柔。好好宠爱自己吧！' },
    { keywords: ['惊喜', '惊喜计划'], response: '想要制造惊喜？我已经为你准备了一份贴心计划，让我们一起创造美好的回忆吧！' },
    { keywords: ['放松', '休闲'], response: '慢下来，感受生活的美好。放松不是偷懒，而是为了更好地前行。' }
  ]
};

// 安慰语录库
const comfortResponses = {
  // 负面情绪安慰
  negative: [
    '抱抱你~ 每个人都会有低潮期，但这不代表你不够好。给自己一些时间和耐心。',
    '难过的时候，允许自己脆弱一会儿。阴天之后总会放晴的，我会一直在这里陪着你。',
    '你已经很努力了，累了就休息一下吧。生活不只有眼前的苟且，还有诗和远方的田野。',
    '别担心，所有的困难都是在为将来的惊喜做铺垫。你比自己想象的更坚强！',
    '有时候我们需要的不是建议，而是一个温暖的拥抱。所以，抱抱~ 一切都会好起来的。'
  ],
  // 积极情绪回应
  positive: [
    '看到你开心，我也忍不住嘴角上扬了呢！愿你的每一天都像今天一样美好~',
    '开心的情绪是会传染的！谢谢你把这份快乐分享给我。',
    '为你感到高兴！继续保持这份美好的心情吧~',
    '笑容是你最美的装饰，希望你能常常拥有。',
    '正能量满满！你的快乐就是这个世界的小太阳。'
  ],
  // 中性情绪
  neutral: [
    '感谢你愿意分享心情。无论今天如何，明天都是崭新的开始。',
    '生活就像天气，有晴天也有雨天，但每一种都有它独特的美。',
    '平淡也是生活的一种味道，宁静致远，细水长流。',
    '你的心情我收到了，无论何时，这里都是你可以倾诉的港湾。',
    '每一天都是独一无二的，愿你在这份独特中找到属于自己的节奏。'
  ]
};

// 惊喜计划库
const surprisePlans = {
  negative: {
    title: "治愈系慢生活",
    description: "给自己一个慢下来的理由，用心感受生活的温柔",
    plan: [
      "在咖啡馆里读一本喜欢的书",
      "去花店买一束自己喜欢的花",
      "在公园长椅上看日落",
      "回家泡一个香氛浴",
      "写一封给未来自己的信"
    ]
  },
  positive: {
    title: "浪漫庆祝夜",
    description: "为这份美好庆祝，创造难忘的回忆",
    plan: [
      "预订一家浪漫餐厅",
      "准备一份小礼物给自己",
      "去城市最高点看夜景",
      "在星空下许个愿",
      "记录今天的美好时光"
    ]
  },
  reward: {
    title: "奢华犒赏日",
    description: "好好宠爱自己，享受生活的美好",
    plan: [
      "睡到自然醒，不做闹钟的奴隶",
      "去高级SPA馆享受专业护理",
      "购物狂欢，买下心仪已久的物品",
      "品尝米其林餐厅的美味",
      "看一场豪华影院的首映电影"
    ]
  }
};

// DOM元素
const moodInput = document.getElementById('moodInput');
const submitMood = document.getElementById('submitMood');
const comfortSection = document.getElementById('comfortSection');
const comfortCard = document.getElementById('comfortCard');
const recommendationSection = document.getElementById('recommendationSection');
const recommendationCards = document.getElementById('recommendationCards');
const routeSection = document.getElementById('routeSection');
const routeContainer = document.getElementById('routeContainer');
const surpriseSection = document.getElementById('surpriseSection');
const surpriseCard = document.getElementById('surpriseCard');
const diarySection = document.getElementById('diarySection');
const diaryTimeline = document.getElementById('diaryTimeline');
const clearDiary = document.getElementById('clearDiary');

// 情绪识别函数
function detectMood(text) {
  // 转换为小写便于匹配
  const lowerText = text.toLowerCase();
  
  // 检查负面情绪
  for (const item of moodKeywords.negative) {
    for (const keyword of item.keywords) {
      if (lowerText.includes(keyword)) {
        return {
          type: 'negative',
          response: item.response
        };
      }
    }
  }
  
  // 检查正面情绪
  for (const item of moodKeywords.positive) {
    for (const keyword of item.keywords) {
      if (lowerText.includes(keyword)) {
        return {
          type: 'positive',
          response: item.response
        };
      }
    }
  }
  
  // 如果没有匹配到特定关键词，根据情感倾向判断
  if (lowerText.includes('累') || lowerText.includes('压力') || lowerText.includes('焦虑') || 
      lowerText.includes('难过') || lowerText.includes('沮丧')) {
    return { type: 'negative' };
  }
  
  if (lowerText.includes('庆祝') || lowerText.includes('成功') || lowerText.includes('开心') || 
      lowerText.includes('高兴') || lowerText.includes('惊喜')) {
    return { type: 'positive' };
  }
  
  if (lowerText.includes('犒劳') || lowerText.includes('奖励') || lowerText.includes('放松')) {
    return { type: 'reward' };
  }
  
  // 默认返回中性情绪
  return { type: 'neutral' };
}

// 获取安慰语
function getComfortResponse(mood) {
  if (mood.response) {
    return mood.response;
  }
  
  const responses = comfortResponses[mood.type] || comfortResponses.neutral;
  const randomIndex = Math.floor(Math.random() * responses.length);
  return responses[randomIndex];
}

// 显示安慰内容
function showComfort(mood) {
  const comfortText = getComfortResponse(mood);
  
  comfortCard.innerHTML = `
    <div class="comfort-content">
      <h3>给你一个温暖的抱抱 🤗</h3>
      <p>${comfortText}</p>
    </div>
  `;
  
  comfortSection.classList.remove('hidden');
  comfortSection.scrollIntoView({ behavior: 'smooth' });
  
  return comfortText;
}

// 显示推荐地点（使用高德地图API）
async function showRecommendations(moodType) {
  try {
    // 显示加载状态
    recommendationCards.innerHTML = '<div class="loading">正在为你寻找合适的地点...</div>';
    recommendationSection.classList.remove('hidden');
    
    // 获取用户当前位置
    const position = await gaodeAPI.getCurrentPosition();
    
    // 根据情绪类型推荐地点
    const places = await gaodeAPI.recommendPlacesByMood(moodType, position.position);
    
    // 渲染推荐地点
    renderRecommendations(places);
  } catch (error) {
    console.error('获取推荐地点时出错:', error);
    // 出错时显示默认推荐
    showDefaultRecommendations(moodType);
  }
}

// 渲染推荐地点
function renderRecommendations(places) {
  recommendationCards.innerHTML = '';
  
  if (places.length === 0) {
    recommendationCards.innerHTML = '<p class="no-results">抱歉，附近没有找到相关地点。</p>';
    return;
  }
  
  places.forEach(place => {
    const card = document.createElement('div');
    card.className = 'card recommendation-card';
    
    // 获取第一张图片，如果没有则使用默认图片
    const photoUrl = place.photos && place.photos.length > 0 
      ? place.photos[0].url 
      : 'https://picsum.photos/300/200?random=' + place.id;
    
    card.innerHTML = `
      <img src="${photoUrl}" alt="${place.name}" class="place-image">
      <div class="place-info">
        <h3>${place.name}</h3>
        <p>${place.address || '地址信息暂无'}</p>
        <div class="place-meta">
          <span class="rating">★ ${place.rating || '暂无评分'}</span>
          <span class="distance">${place.distance ? (place.distance > 1000 ? (place.distance/1000).toFixed(1) + 'km' : place.distance + 'm') : '距离未知'}</span>
        </div>
      </div>
    `;
    recommendationCards.appendChild(card);
  });
}

// 显示默认推荐（当API调用失败时）
function showDefaultRecommendations(moodType) {
  // 地点推荐库（模拟数据）
  const placeRecommendations = {
    // 心情低落时的推荐
    negative: [
      {
        name: "静心书店",
        description: "安静舒适的书店，有丰富的书籍和温馨的阅读角落。",
        image: "https://picsum.photos/seed/bookstore/300/200",
        rating: 4.7,
        distance: "500m",
        type: "书店"
      },
      {
        name: "晨曦咖啡",
        description: "环境优雅的咖啡馆，有手冲咖啡和舒缓的音乐。",
        image: "https://picsum.photos/seed/cafe/300/200",
        rating: 4.5,
        distance: "800m",
        type: "咖啡馆"
      },
      {
        name: "城市绿洲公园",
        description: "市中心的绿洲，有湖泊和步道，适合散步放松。",
        image: "https://picsum.photos/seed/park/300/200",
        rating: 4.8,
        distance: "1.2km",
        type: "公园"
      }
    ],
    // 想庆祝时的推荐
    positive: [
      {
        name: "浪漫法餐厅",
        description: "精致的法式料理，优雅的环境适合庆祝特殊时刻。",
        image: "https://picsum.photos/seed/restaurant/300/200",
        rating: 4.9,
        distance: "1.5km",
        type: "餐厅"
      },
      {
        name: "城市夜景观景台",
        description: "俯瞰城市全景的最佳位置，夜景迷人。",
        image: "https://picsum.photos/seed/nightview/300/200",
        rating: 4.6,
        distance: "2.3km",
        type: "景点"
      },
      {
        name: "星空酒吧",
        description: "高端酒吧，有调酒师现场表演和精选酒单。",
        image: "https://picsum.photos/seed/bar/300/200",
        rating: 4.7,
        distance: "1.8km",
        type: "酒吧"
      }
    ],
    // 想犒劳自己时的推荐
    reward: [
      {
        name: "美食广场",
        description: "汇集各地美食的小吃天堂，满足你的味蕾。",
        image: "https://picsum.photos/seed/foodcourt/300/200",
        rating: 4.4,
        distance: "900m",
        type: "美食"
      },
      {
        name: "购物中心",
        description: "一站式购物天堂，有各种品牌店和娱乐设施。",
        image: "https://picsum.photos/seed/mall/300/200",
        rating: 4.3,
        distance: "1.7km",
        type: "购物"
      },
      {
        name: "SPA会所",
        description: "专业的按摩和护理服务，让你彻底放松身心。",
        image: "https://picsum.photos/seed/spa/300/200",
        rating: 4.8,
        distance: "1.1km",
        type: "美容"
      }
    ]
  };

  const places = placeRecommendations[moodType] || placeRecommendations.negative;
  
  recommendationCards.innerHTML = '';
  
  places.forEach(place => {
    const card = document.createElement('div');
    card.className = 'card recommendation-card';
    card.innerHTML = `
      <img src="${place.image}" alt="${place.name}" class="place-image">
      <div class="place-info">
        <h3>${place.name}</h3>
        <p>${place.description}</p>
        <div class="place-meta">
          <span class="rating">★ ${place.rating}</span>
          <span class="distance">${place.distance}</span>
        </div>
      </div>
    `;
    recommendationCards.appendChild(card);
  });
}

// 显示路线规划（使用高德地图API）
async function showRoute(moodType) {
  try {
    // 显示加载状态
    routeContainer.innerHTML = '<div class="loading">正在为你规划专属路线...</div>';
    routeSection.classList.remove('hidden');
    
    // 获取用户当前位置
    const position = await gaodeAPI.getCurrentPosition();
    
    // 初始化地图
    const mapContainer = document.createElement('div');
    mapContainer.id = 'route-map';
    mapContainer.className = 'route-map';
    routeContainer.innerHTML = '';
    routeContainer.appendChild(mapContainer);
    
    await gaodeAPI.initMap('route-map', {
      center: position.position,
      zoom: 14
    });
    
    // 这里可以添加更复杂的路线规划逻辑
    // 暂时显示简单的路线步骤
    renderRouteSteps(moodType);
  } catch (error) {
    console.error('路线规划时出错:', error);
    // 出错时显示默认路线
    showDefaultRoute(moodType);
  }
}

// 渲染路线步骤
function renderRouteSteps(moodType) {
  // 情绪化路线规划
  const moodRoutes = {
    negative: [
      { name: "温暖咖啡馆", description: "先去喝杯热饮，让心情暖起来" },
      { name: "宁静书店", description: "找个安静角落，翻阅喜欢的书籍" },
      { name: "湖边公园", description: "沿着湖边慢慢散步，呼吸新鲜空气" },
      { name: "甜品店", description: "用一块小蛋糕奖励今天的自己" }
    ],
    positive: [
      { name: "精品餐厅", description: "在优雅环境中享受精致美食" },
      { name: "艺术展览", description: "欣赏艺术作品，提升审美体验" },
      { name: "城市观景台", description: "俯瞰城市美景，留下美好回忆" },
      { name: "音乐会", description: "沉浸在音乐的海洋中" }
    ],
    reward: [
      { name: "网红餐厅", description: "品尝特色美食，满足味蕾享受" },
      { name: "购物中心", description: "挑选心仪物品，犒劳努力的自己" },
      { name: "电影院", description: "看一场电影，享受视听盛宴" },
      { name: "KTV", description: "放声歌唱，释放内心激情" }
    ]
  };
  
  const steps = moodRoutes[moodType] || moodRoutes.negative;
  
  // 创建路线步骤
  const stepsContainer = document.createElement('div');
  stepsContainer.className = 'route-steps';
  
  steps.forEach((step, index) => {
    const stepElement = document.createElement('div');
    stepElement.className = 'route-step';
    stepElement.innerHTML = `
      <div class="route-step-number">${index + 1}</div>
      <h4>${step.name}</h4>
      <p>${step.description}</p>
    `;
    stepsContainer.appendChild(stepElement);
  });
  
  routeContainer.appendChild(stepsContainer);
}

// 显示默认路线（当API调用失败时）
function showDefaultRoute(moodType) {
  // 情绪化路线规划
  const moodRoutes = {
    negative: [
      { name: "温暖咖啡馆", description: "先去喝杯热饮，让心情暖起来" },
      { name: "宁静书店", description: "找个安静角落，翻阅喜欢的书籍" },
      { name: "湖边公园", description: "沿着湖边慢慢散步，呼吸新鲜空气" },
      { name: "甜品店", description: "用一块小蛋糕奖励今天的自己" }
    ],
    positive: [
      { name: "精品餐厅", description: "在优雅环境中享受精致美食" },
      { name: "艺术展览", description: "欣赏艺术作品，提升审美体验" },
      { name: "城市观景台", description: "俯瞰城市美景，留下美好回忆" },
      { name: "音乐会", description: "沉浸在音乐的海洋中" }
    ],
    reward: [
      { name: "网红餐厅", description: "品尝特色美食，满足味蕾享受" },
      { name: "购物中心", description: "挑选心仪物品，犒劳努力的自己" },
      { name: "电影院", description: "看一场电影，享受视听盛宴" },
      { name: "KTV", description: "放声歌唱，释放内心激情" }
    ]
  };
  
  const steps = moodRoutes[moodType] || moodRoutes.negative;
  
  // 创建地图容器（模拟）
  const mapElement = document.createElement('div');
  mapElement.className = 'route-map';
  mapElement.textContent = '路线地图将在这里显示';
  
  // 创建路线步骤
  const stepsContainer = document.createElement('div');
  stepsContainer.className = 'route-steps';
  
  steps.forEach((step, index) => {
    const stepElement = document.createElement('div');
    stepElement.className = 'route-step';
    stepElement.innerHTML = `
      <div class="route-step-number">${index + 1}</div>
      <h4>${step.name}</h4>
      <p>${step.description}</p>
    `;
    stepsContainer.appendChild(stepElement);
  });
  
  routeContainer.innerHTML = '';
  routeContainer.appendChild(mapElement);
  routeContainer.appendChild(stepsContainer);
  
  routeSection.classList.remove('hidden');
}

// 显示惊喜计划
function showSurprise(moodType) {
  const plan = surprisePlans[moodType] || surprisePlans.negative;
  
  surpriseCard.innerHTML = `
    <div class="surprise-content">
      <h3>${plan.title}</h3>
      <p>${plan.description}</p>
      <p>今天也要好好犒劳自己哦 💙</p>
      <div class="plan-details">
        <h4>小确幸计划：</h4>
        <ul>
          ${plan.plan.map(item => `<li>${item}</li>`).join('')}
        </ul>
      </div>
    </div>
  `;
  
  surpriseSection.classList.remove('hidden');
}

// 情绪日记功能
let moodDiary = [];

// 保存日记条目到本地存储
function saveDiaryToLocalStorage() {
  localStorage.setItem('moodDiary', JSON.stringify(moodDiary));
}

// 从本地存储加载日记条目
function loadDiaryFromLocalStorage() {
  const storedDiary = localStorage.getItem('moodDiary');
  if (storedDiary) {
    moodDiary = JSON.parse(storedDiary);
  }
}

// 添加日记条目
function addDiaryEntry(moodText, moodType, comfortText) {
  const entry = {
    id: Date.now(),
    date: new Date().toLocaleString('zh-CN'),
    moodText: moodText,
    moodType: moodType,
    comfortText: comfortText
  };
  
  moodDiary.unshift(entry); // 添加到数组开头
  saveDiaryToLocalStorage();
  renderDiary();
}

// 渲染日记
function renderDiary() {
  diaryTimeline.innerHTML = '';
  
  if (moodDiary.length === 0) {
    diaryTimeline.innerHTML = '<p class="no-results">还没有情绪日记哦，快来记录你的心情吧！</p>';
    return;
  }
  
  moodDiary.forEach(entry => {
    const entryElement = document.createElement('div');
    entryElement.className = 'diary-entry';
    entryElement.innerHTML = `
      <div class="diary-date">${entry.date}</div>
      <div class="diary-mood">心情：${entry.moodText}</div>
      <div class="diary-comfort">安慰：${entry.comfortText}</div>
    `;
    diaryTimeline.appendChild(entryElement);
  });
  
  diarySection.classList.remove('hidden');
}

// 清空日记
function clearDiaryEntries() {
  if (confirm('确定要清空所有情绪日记吗？')) {
    moodDiary = [];
    saveDiaryToLocalStorage();
    renderDiary();
  }
}

// 处理用户输入的心情
async function processMood() {
  const moodText = moodInput.value.trim();
  
  if (!moodText) {
    alert('请输入你的心情哦~');
    return;
  }
  
  // 识别情绪
  const mood = detectMood(moodText);
  
  // 显示安慰
  const comfortText = showComfort(mood);
  
  // 显示推荐地点
  showRecommendations(mood.type);
  
  // 显示路线规划
  showRoute(mood.type);
  
  // 显示惊喜计划
  showSurprise(mood.type);
  
  // 添加到情绪日记
  addDiaryEntry(moodText, mood.type, comfortText);
  
  // 清空输入框
  moodInput.value = '';
}

// 事件监听
submitMood.addEventListener('click', processMood);
clearDiary.addEventListener('click', clearDiaryEntries);

// 回车键提交（Ctrl+Enter）
moodInput.addEventListener('keydown', (e) => {
  if (e.ctrlKey && e.key === 'Enter') {
    processMood();
  }
});

// 初始化应用
document.addEventListener('DOMContentLoaded', async () => {
  // 添加标题动画类
  const title = document.querySelector('.app-title');
  if (title) {
    setTimeout(() => {
      title.classList.add('pulse');
    }, 1000);
  }
  
  // 加载情绪日记
  loadDiaryFromLocalStorage();
  renderDiary();
  
  // 初始化高德地图API
  try {
    await gaodeAPI.init();
    console.log('高德地图API初始化成功');
  } catch (error) {
    console.error('高德地图API初始化失败:', error);
    // 显示提示信息，建议用户注册API密钥
    alert('地图功能需要配置高德地图API密钥才能正常使用。请在gaode-api.js中配置您的API密钥。');
  }
});