import React, { useState } from 'react';
import DayCard from '../components/DayCard';
import './ItineraryPage.css';

const ItineraryPage = () => {
  const [selectedDay, setSelectedDay] = useState(1);

  // Sample data for the 4-day itinerary
  const itineraryData = [
    {
      day: 1,
      title: "第一天：武汉经典之旅",
      date: "10月1日",
      weather: "晴 25-30°C",
      activities: [
        {
          time: "09:00",
          name: "黄鹤楼",
          description: "武汉地标建筑，享有“天下江山第一楼“之称",
          image: "https://picsum.photos/seed/huanghelou/600/400"
        },
        {
          time: "12:30",
          name: "户部巷美食街",
          description: "品尝武汉特色小吃，如热干面、豆皮等",
          image: "https://picsum.photos/seed/foodstreet/600/400"
        },
        {
          time: "15:00",
          name: "长江大桥",
          description: "万里长江第一桥，欣赏江景和城市风光",
          image: "https://picsum.photos/seed/yangtze/600/400"
        }
      ]
    },
    {
      day: 2,
      title: "第二天：东湖生态之旅",
      date: "10月2日",
      weather: "多云 23-28°C",
      activities: [
        {
          time: "09:30",
          name: "东湖风景区",
          description: "中国最大城中湖，骑行或漫步湖边绿道",
          image: "https://picsum.photos/seed/eastlake/600/400"
        },
        {
          time: "12:00",
          name: "湖北省博物馆",
          description: "欣赏曾侯乙编钟等珍贵文物",
          image: "https://picsum.photos/seed/museum/600/400"
        },
        {
          time: "15:30",
          name: "楚河汉街",
          description: "现代商业街区，购物和休闲的好去处",
          image: "https://picsum.photos/seed/hanstreet/600/400"
        }
      ]
    },
    {
      day: 3,
      title: "第三天：文化体验之旅",
      date: "10月3日",
      weather: "晴 24-29°C",
      activities: [
        {
          time: "10:00",
          name: "武汉大学",
          description: "中国最美校园之一，观赏樱花（季节性）或建筑",
          image: "https://picsum.photos/seed/university/600/400"
        },
        {
          time: "13:00",
          name: "昙华林",
          description: "文艺小资聚集地，品尝咖啡和甜品",
          image: "https://picsum.photos/seed/tanhualin/600/400"
        },
        {
          time: "16:00",
          name: "江汉路步行街",
          description: "百年商业老街，欣赏欧式建筑风格",
          image: "https://picsum.photos/seed/jianghan/600/400"
        }
      ]
    },
    {
      day: 4,
      title: "第四天：休闲购物之旅",
      date: "10月4日",
      weather: "多云 22-27°C",
      activities: [
        {
          time: "10:30",
          name: "汉口江滩",
          description: "沿江休闲观光带，欣赏两江交汇美景",
          image: "https://picsum.photos/seed/riverbeach/600/400"
        },
        {
          time: "13:30",
          name: "光谷广场",
          description: "现代化购物中心，体验科技与商业融合",
          image: "https://picsum.photos/seed/opticsvalley/600/400"
        },
        {
          time: "16:00",
          name: "黎黄陂路",
          description: "充满异国风情的历史文化街区",
          image: "https://picsum.photos/seed/lhuangpi/600/400"
        }
      ]
    }
  ];

  return (
    <div className="itinerary-page">
      <div className="navigation">
        {itineraryData.map((day) => (
          <button
            key={day.day}
            className={`nav-button ${selectedDay === day.day ? 'active' : ''}`}
            onClick={() => setSelectedDay(day.day)}
          >
            第{day.day}天
          </button>
        ))}
      </div>

      <div className="day-details">
        {itineraryData
          .filter(day => day.day === selectedDay)
          .map(day => (
            <div key={day.day}>
              <h2>{day.title}</h2>
              <p className="date-weather">{day.date} | {day.weather}</p>
              <div className="activities-list">
                {day.activities.map((activity, index) => (
                  <DayCard 
                    key={index}
                    time={activity.time}
                    name={activity.name}
                    description={activity.description}
                    image={activity.image}
                  />
                ))}
              </div>
            </div>
          ))}
      </div>
    </div>
  );
};

export default ItineraryPage;