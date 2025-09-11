// 情绪日记数据存储
let moodDiary = [];
// 推荐地点历史
let recommendedPlaces = [];

// 初始化地图变量
let map;
let userLocation = null;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化定位功能
    initGeolocation();
    
    // 绑定心情提交事件
    document.getElementById('mood-submit').addEventListener('click', handleMoodSubmit);
    
    // 绑定惊喜按钮事件
    document.getElementById('surprise-button').addEventListener('click', generateSurprisePlan);
    
    // 绑定情绪日记按钮事件
    document.getElementById('diary-button').addEventListener('click', toggleDiary);
});

// 初始化定位功能
function initGeolocation() {
    // 检查浏览器是否支持地理定位
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            // 定位成功回调
            function(position) {
                userLocation = {
                    longitude: position.coords.longitude,
                    latitude: position.coords.latitude
                };
                
                // 显示位置信息
                displayLocationInfo(userLocation);
                
                // 初始化地图
                initMap(userLocation);
            },
            // 定位失败回调
            function(error) {
                handleGeolocationError(error);
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            }
        );
    } else {
        // 浏览器不支持地理定位
        handleGeolocationUnsupported();
    }
}

// 显示位置信息
function displayLocationInfo(location) {
    const locationInfo = document.getElementById('location-info');
    locationInfo.innerHTML = `
        <p>经度: ${location.longitude.toFixed(6)}</p>
        <p>纬度: ${location.latitude.toFixed(6)}</p>
        <p>状态: 定位成功</p>
    `;
}

// 初始化地图
function initMap(location) {
    // 显示地图容器
    document.getElementById('map-container').style.display = 'block';
    
    // 创建地图实例
    map = new AMap.Map('map-container', {
        zoom: 14,
        center: [location.longitude, location.latitude]
    });
    
    // 添加定位标记
    const marker = new AMap.Marker({
        position: [location.longitude, location.latitude],
        title: '您的位置',
        map: map
    });
    
    // 添加地图控件
    map.addControl(new AMap.Scale());
    map.addControl(new AMap.ToolBar());
    
    // 显示心情地图
    displayMoodMap();
}

// 处理定位错误
function handleGeolocationError(error) {
    const locationInfo = document.getElementById('location-info');
    
    switch(error.code) {
        case error.PERMISSION_DENIED:
            locationInfo.innerHTML = `
                <p>您拒绝了位置请求。</p>
                <p>请手动输入城市或位置关键词：</p>
                <input type="text" id="manual-location" placeholder="请输入城市或位置">
                <button onclick="handleManualLocation()">确定</button>
            `;
            break;
        case error.POSITION_UNAVAILABLE:
            locationInfo.innerHTML = '<p>位置信息不可用。</p>';
            break;
        case error.TIMEOUT:
            locationInfo.innerHTML = '<p>获取位置超时。</p>';
            break;
        default:
            locationInfo.innerHTML = '<p>获取位置时发生未知错误。</p>';
            break;
    }
}

// 处理不支持地理定位的情况
function handleGeolocationUnsupported() {
    const locationInfo = document.getElementById('location-info');
    locationInfo.innerHTML = `
        <p>您的浏览器不支持地理定位。</p>
        <p>请手动输入城市或位置关键词：</p>
        <input type="text" id="manual-location" placeholder="请输入城市或位置">
        <button onclick="handleManualLocation()">确定</button>
    `;
}

// 处理手动输入位置
function handleManualLocation() {
    const locationInput = document.getElementById('manual-location');
    const locationText = locationInput.value.trim();
    
    if (locationText) {
        // 这里应该调用高德地图的地理编码API将文本转换为经纬度
        // 为简化示例，我们使用一个虚拟的位置
        userLocation = {
            longitude: 116.397428, // 北京天安门经度
            latitude: 39.90923 // 北京天安门纬度
        };
        
        // 显示位置信息
        displayLocationInfo(userLocation);
        
        // 初始化地图
        initMap(userLocation);
    } else {
        alert('请输入有效的城市或位置信息');
    }
}

// 处理心情提交
function handleMoodSubmit() {
    const moodInput = document.getElementById('mood-input');
    const moodText = moodInput.value.trim();
    
    if (moodText) {
        // 识别情绪并生成安慰语
        const comfortMessage = generateComfortMessage(moodText);
        
        // 显示安慰语
        displayComfortMessage(comfortMessage);
        
        // 根据心情生成推荐
        generateRecommendations(moodText);
        
        // 保存到情绪日记
        saveToDiary(moodText, comfortMessage);
    } else {
        alert('请输入您的心情');
    }
}

// 生成安慰语
function generateComfortMessage(mood) {
    // 简单的情绪识别和安慰语生成
    // 在实际应用中，可以使用更复杂的NLP技术
    if (mood.includes('累') || mood.includes('疲惫')) {
        return '辛苦了！累了就休息一下吧，给自己一个拥抱。世界很美好，你也是。💙';
    } else if (mood.includes('不好') || mood.includes('沮丧')) {
        return '心情不好是正常的，每个人都会有这样的时刻。愿你被温柔以待，明天会更好的。💚';
    } else if (mood.includes('放松') || mood.includes('轻松')) {
        return '想要放松一下是很好的想法呢！享受这份宁静时光，让心灵得到充分的休憩。💛';
    } else if (mood.includes('开心') || mood.includes('高兴')) {
        return '看到你开心我也很开心！继续保持这份好心情，让快乐成为生活的常态。💜';
    } else {
        return '感谢你分享心情。无论何时，都要记得照顾好自己哦！🧡';
    }
}

// 显示安慰语
function displayComfortMessage(message) {
    const comfortElement = document.getElementById('comfort-message');
    comfortElement.innerHTML = `<p>${message}</p>`;
    comfortElement.style.display = 'block';
}

// 生成推荐
function generateRecommendations(mood) {
    // 根据心情生成不同的推荐
    let recommendations = [];
    
    if (mood.includes('不好') || mood.includes('沮丧') || mood.includes('累')) {
        recommendations = [
            {
                name: '静心咖啡馆',
                description: '一家安静舒适的咖啡馆，适合放松心情',
                image: 'https://picsum.photos/300/200?random=1',
                rating: 4.8,
                hours: '08:00-22:00',
                longitude: userLocation.longitude + (Math.random() - 0.5) * 0.02,
                latitude: userLocation.latitude + (Math.random() - 0.5) * 0.02
            },
            {
                name: '城市绿洲公园',
                description: '市中心的绿洲，是散步和冥想的好地方',
                image: 'https://picsum.photos/300/200?random=2',
                rating: 4.6,
                hours: '06:00-23:00',
                longitude: userLocation.longitude + (Math.random() - 0.5) * 0.02,
                latitude: userLocation.latitude + (Math.random() - 0.5) * 0.02
            },
            {
                name: '书香书店',
                description: '充满文艺气息的书店，可以安静阅读',
                image: 'https://picsum.photos/300/200?random=3',
                rating: 4.7,
                hours: '09:00-21:00',
                longitude: userLocation.longitude + (Math.random() - 0.5) * 0.02,
                latitude: userLocation.latitude + (Math.random() - 0.5) * 0.02
            }
        ];
    } else if (mood.includes('庆祝') || mood.includes('开心')) {
        recommendations = [
            {
                name: '浪漫法餐厅',
                description: '精致的法式料理，适合庆祝特殊时刻',
                image: 'https://picsum.photos/300/200?random=4',
                rating: 4.9,
                hours: '11:00-22:00',
                longitude: userLocation.longitude + (Math.random() - 0.5) * 0.02,
                latitude: userLocation.latitude + (Math.random() - 0.5) * 0.02
            },
            {
                name: '城市夜景观景台',
                description: '俯瞰城市全景的最佳位置',
                image: 'https://picsum.photos/300/200?random=5',
                rating: 4.8,
                hours: '18:00-24:00',
                longitude: userLocation.longitude + (Math.random() - 0.5) * 0.02,
                latitude: userLocation.latitude + (Math.random() - 0.5) * 0.02
            }
        ];
    } else {
        recommendations = [
            {
                name: '美食广场',
                description: '各种美食汇集地，满足你的味蕾',
                image: 'https://picsum.photos/300/200?random=6',
                rating: 4.5,
                hours: '10:00-22:00',
                longitude: userLocation.longitude + (Math.random() - 0.5) * 0.02,
                latitude: userLocation.latitude + (Math.random() - 0.5) * 0.02
            },
            {
                name: '购物中心',
                description: '一站式购物天堂，尽情享受购物乐趣',
                image: 'https://picsum.photos/300/200?random=7',
                rating: 4.6,
                hours: '09:00-22:00',
                longitude: userLocation.longitude + (Math.random() - 0.5) * 0.02,
                latitude: userLocation.latitude + (Math.random() - 0.5) * 0.02
            }
        ];
    }
    
    // 保存推荐地点到历史记录
    recommendedPlaces = recommendations;
    
    // 显示推荐
    displayRecommendations(recommendations);
    
    // 生成路线
    generateRoutePlan(recommendations.slice(0, 3));
    
    // 更新心情地图
    displayMoodMap();
}

// 显示推荐
function displayRecommendations(recommendations) {
    const container = document.getElementById('recommendations-container');
    
    // 清空容器
    container.innerHTML = '';
    
    // 创建卡片容器
    const cardsContainer = document.createElement('div');
    cardsContainer.className = 'cards-container';
    
    // 为每个推荐创建卡片
    recommendations.forEach(rec => {
        const card = document.createElement('div');
        card.className = 'recommendation-card';
        card.innerHTML = `
            <img src="${rec.image}" alt="${rec.name}" class="card-image">
            <div class="card-content">
                <h3>${rec.name}</h3>
                <p>${rec.description}</p>
            </div>
            <div class="card-footer">
                <span>评分: ${rec.rating}</span>
                <span>营业时间: ${rec.hours}</span>
            </div>
        `;
        cardsContainer.appendChild(card);
    });
    
    // 添加到容器
    container.appendChild(cardsContainer);
}

// 生成路线计划
function generateRoutePlan(places) {
    const container = document.getElementById('route-container');
    
    // 清空容器
    container.innerHTML = '';
    
    // 创建路线卡片
    const routeCard = document.createElement('div');
    routeCard.className = 'route-card';
    
    // 生成路线步骤
    let stepsHtml = '<div class="route-steps">';
    places.forEach((place, index) => {
        stepsHtml += `<div class="route-step">第${index+1}站: ${place.name}</div>`;
    });
    stepsHtml += '</div>';
    
    routeCard.innerHTML = `
        <h3>为您定制的情绪路线</h3>
        <p>这条路线结合了您的心情和当前位置，希望能为您带来美好的体验。</p>
        ${stepsHtml}
        <button onclick="showDetailedRoute()">查看详细导航</button>
    `;
    
    // 添加到容器
    container.appendChild(routeCard);
}

// 显示详细路线
function showDetailedRoute() {
    alert('在实际应用中，这里会显示详细的导航路线。');
    // 在实际应用中，这里会调用高德地图的路线规划API
}

// 生成惊喜计划
function generateSurprisePlan() {
    const planElement = document.getElementById('surprise-plan');
    
    const plans = [
        '<h3>浪漫夜游计划</h3><p>一起去看城市的夜景，在安静的咖啡馆聊聊天，享受这份宁静与浪漫。</p>',
        '<h3>周末疗愈路线</h3><p>去公园散步，找一家舒适的书店看看书，让心灵得到彻底的放松。</p>',
        '<h3>美食探索之旅</h3><p>去尝试那些一直想吃但没机会的美食，让味蕾带你旅行。</p>'
    ];
    
    const randomPlan = plans[Math.floor(Math.random() * plans.length)];
    planElement.innerHTML = `<div class="comfort-card">${randomPlan}</div>`;
}

// 保存到情绪日记
function saveToDiary(mood, comfortMessage) {
    const entry = {
        id: Date.now(),
        timestamp: new Date().toLocaleString(),
        mood: mood,
        comfortMessage: comfortMessage
    };
    
    moodDiary.push(entry);
    
    // 更新情绪日记显示
    displayDiary();
}

// 显示情绪日记
function displayDiary() {
    const diaryContainer = document.getElementById('diary-entries');
    diaryContainer.innerHTML = '';
    
    if (moodDiary.length === 0) {
        diaryContainer.innerHTML = '<p>暂无日记 entries</p>';
        return;
    }
    
    // 按时间倒序显示
    moodDiary.slice().reverse().forEach(entry => {
        const entryElement = document.createElement('div');
        entryElement.className = 'diary-entry';
        entryElement.innerHTML = `
            <div class="diary-date">${entry.timestamp}</div>
            <div class="diary-mood">心情: ${entry.mood}</div>
            <div class="diary-comfort">安慰语: ${entry.comfortMessage}</div>
        `;
        diaryContainer.appendChild(entryElement);
    });
}

// 切换情绪日记显示
function toggleDiary() {
    const diarySection = document.getElementById('diary-section');
    const button = document.getElementById('diary-button');
    
    if (diarySection.style.display === 'none') {
        diarySection.style.display = 'block';
        button.textContent = '隐藏情绪日记';
        displayDiary();
    } else {
        diarySection.style.display = 'none';
        button.textContent = '查看情绪日记';
    }
}

// 显示心情地图
function displayMoodMap() {
    // 如果地图未初始化或没有推荐地点，直接返回
    if (!map || recommendedPlaces.length === 0) {
        return;
    }
    
    // 清除之前的标记
    map.clearMap();
    
    // 添加用户位置标记
    const userMarker = new AMap.Marker({
        position: [userLocation.longitude, userLocation.latitude],
        title: '您的位置',
        map: map,
        label: {
            content: '您',
            offset: new AMap.Pixel(-5, -5)
        }
    });
    
    // 为每个推荐地点添加标记
    recommendedPlaces.forEach((place, index) => {
        const marker = new AMap.Marker({
            position: [place.longitude, place.latitude],
            title: place.name,
            map: map,
            label: {
                content: `${index + 1}`,
                offset: new AMap.Pixel(-5, -5)
            }
        });
        
        // 添加信息窗口
        const infoWindow = new AMap.InfoWindow({
            content: `<div><strong>${place.name}</strong><br/>评分: ${place.rating}</div>`,
            offset: new AMap.Pixel(0, -30)
        });
        
        // 绑定点击事件
        marker.on('click', function() {
            infoWindow.open(map, marker.getPosition());
        });
    });
}