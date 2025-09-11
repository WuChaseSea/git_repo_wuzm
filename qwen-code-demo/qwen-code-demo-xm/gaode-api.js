// gaode-api.js - 高德地图API集成模块

class GaodeAPI {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.map = null;
    this.placeSearch = null;
    this.geolocation = null;
  }

  // 初始化高德地图API
  init() {
    return new Promise((resolve, reject) => {
      // 动态加载高德地图JS API
      const script = document.createElement('script');
      script.type = 'text/javascript';
      script.src = `https://webapi.amap.com/maps?v=1.4.15&key=${this.apiKey}&plugin=AMap.PlaceSearch,AMap.Geolocation`;
      script.onload = () => {
        resolve();
      };
      script.onerror = () => {
        reject(new Error('Failed to load Gaode Maps API'));
      };
      document.head.appendChild(script);
    });
  }

  // 初始化地图组件
  initMap(containerId, options = {}) {
    return new Promise((resolve) => {
      // 等待AMap对象加载完成
      const checkAMap = setInterval(() => {
        if (window.AMap) {
          clearInterval(checkAMap);
          this.map = new AMap.Map(containerId, {
            zoom: 11,
            center: options.center || [116.397428, 39.90923], // 默认北京天安门
            ...options
          });
          
          // 初始化地点搜索插件
          AMap.plugin(['AMap.PlaceSearch'], () => {
            this.placeSearch = new AMap.PlaceSearch({
              pageSize: 10,
              pageIndex: 1,
              city: "全国", // 兴趣点城市
              citylimit: false, // 是否强制限制在设置的城市内
              map: this.map, // 展现结果的地图实例
              panel: null, // 结果列表将在此容器中进行展示
              autoFitView: true // 是否自动调整地图视野使绘制的Marker点都处于视口的可见范围
            });
            
            resolve(this.map);
          });
          
          // 初始化定位插件
          AMap.plugin(['AMap.Geolocation'], () => {
            this.geolocation = new AMap.Geolocation({
              enableHighAccuracy: true, // 是否使用高精度定位
              timeout: 10000, // 超过10秒后停止定位
              buttonPosition: 'RB', // 定位按钮的停靠位置
              buttonOffset: new AMap.Pixel(10, 20), // 定位按钮与设置位置的偏移量
              zoomToAccuracy: true // 定位成功后是否自动调整地图视野到定位点
            });
          });
        }
      }, 100);
    });
  }

  // 获取用户当前位置
  getCurrentPosition() {
    return new Promise((resolve, reject) => {
      if (!this.geolocation) {
        reject(new Error('Geolocation plugin not initialized'));
        return;
      }
      
      this.geolocation.getCurrentPosition((status, result) => {
        if (status === 'complete') {
          resolve({
            position: [result.position.lng, result.position.lat],
            address: result.formattedAddress
          });
        } else {
          reject(new Error(result.message));
        }
      });
    });
  }

  // 搜索附近的地点
  searchNearby(keyword, center, radius = 3000) {
    return new Promise((resolve, reject) => {
      if (!this.placeSearch) {
        reject(new Error('PlaceSearch plugin not initialized'));
        return;
      }
      
      this.placeSearch.searchNearBy(keyword, center, radius, (status, result) => {
        if (status === 'complete') {
          resolve(result.poiList.pois);
        } else {
          reject(new Error(result.info));
        }
      });
    });
  }

  // 根据情绪类型推荐地点
  async recommendPlacesByMood(moodType, center, radius = 3000) {
    // 根据情绪类型定义搜索关键词
    const moodKeywords = {
      negative: ['书店', '咖啡馆', '公园', '图书馆', '茶馆'],
      positive: ['餐厅', '酒吧', 'KTV', '电影院', '夜景观景台'],
      reward: ['购物中心', '美食广场', 'SPA', '高档餐厅', '娱乐场所']
    };
    
    const keywords = moodKeywords[moodType] || moodKeywords.negative;
    const allResults = [];
    
    // 搜索每个关键词
    for (const keyword of keywords) {
      try {
        const results = await this.searchNearby(keyword, center, radius);
        allResults.push(...results);
      } catch (error) {
        console.warn(`搜索关键词"${keyword}"时出错:`, error);
      }
    }
    
    // 去重并限制结果数量
    const uniqueResults = [];
    const seenIds = new Set();
    
    for (const place of allResults) {
      if (!seenIds.has(place.id)) {
        seenIds.add(place.id);
        uniqueResults.push({
          id: place.id,
          name: place.name,
          address: place.address,
          location: place.location,
          tel: place.tel,
          distance: place.distance,
          businessArea: place.businessArea,
          adcode: place.adcode,
          photos: place.photos || [],
          rating: Math.floor(Math.random() * 20 + 30) / 10 // 模拟评分3.0-5.0
        });
      }
    }
    
    // 按距离排序并返回前6个结果
    return uniqueResults
      .sort((a, b) => a.distance - b.distance)
      .slice(0, 6);
  }

  // 绘制路线
  drawRoute(start, end) {
    return new Promise((resolve, reject) => {
      AMap.plugin(['AMap.Driving'], () => {
        const driving = new AMap.Driving({
          map: this.map,
          panel: null
        });
        
        driving.search(start, end, (status, result) => {
          if (status === 'complete') {
            resolve(result);
          } else {
            reject(new Error(result.info));
          }
        });
      });
    });
  }
}

// 高德地图API密钥配置
// 请访问 https://console.amap.com/dev/key/app 创建应用并获取API密钥
// 替换下面的 'YOUR_GAODE_API_KEY_HERE' 为你的实际API密钥
const GAODE_API_KEY = 'YOUR_GAODE_API_KEY_HERE';

// 创建API实例
const gaodeAPI = new GaodeAPI(GAODE_API_KEY);

// 导出模块
export { gaodeAPI, GaodeAPI };