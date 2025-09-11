import React, { useState, useEffect } from 'react';
import './WeatherPage.css';

const WeatherPage = () => {
  const [weatherData, setWeatherData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Mock weather data for Wuhan during National Day
  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      const mockWeatherData = {
        location: "武汉",
        today: {
          date: "2023年10月1日",
          condition: "晴",
          icon: "☀️",
          temperature: "28°C",
          high: "30°C",
          low: "22°C",
          humidity: "65%",
          wind: "东南风 3级"
        },
        forecast: [
          {
            day: "明天",
            date: "10月2日",
            condition: "多云",
            icon: "☁️",
            high: "28°C",
            low: "21°C"
          },
          {
            day: "后天",
            date: "10月3日",
            condition: "晴",
            icon: "☀️",
            high: "29°C",
            low: "22°C"
          },
          {
            day: "周四",
            date: "10月4日",
            condition: "多云",
            icon: "☁️",
            high: "27°C",
            low: "20°C"
          }
        ],
        tips: [
          "国庆期间人流量较大，建议提前预约热门景点",
          "武汉早晚温差较大，请准备薄外套",
          "多云天气适合户外活动，记得做好防晒"
        ]
      };
      setWeatherData(mockWeatherData);
      setLoading(false);
    }, 1000);
  }, []);

  if (loading) {
    return (
      <div className="weather-page">
        <h2>天气信息加载中...</h2>
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <div className="weather-page">
      <h2>武汉天气预报</h2>
      
      <div className="current-weather">
        <div className="weather-card">
          <h3>{weatherData.today.date}</h3>
          <div className="weather-main">
            <span className="weather-icon">{weatherData.today.icon}</span>
            <div className="temp-info">
              <div className="current-temp">{weatherData.today.temperature}</div>
              <div className="condition">{weatherData.today.condition}</div>
            </div>
          </div>
          <div className="weather-details">
            <p>最高温度: {weatherData.today.high}</p>
            <p>最低温度: {weatherData.today.low}</p>
            <p>湿度: {weatherData.today.humidity}</p>
            <p>风力: {weatherData.today.wind}</p>
          </div>
        </div>
      </div>
      
      <div className="forecast">
        <h3>未来几天预报</h3>
        <div className="forecast-cards">
          {weatherData.forecast.map((day, index) => (
            <div key={index} className="forecast-card">
              <h4>{day.day}</h4>
              <p>{day.date}</p>
              <div className="forecast-icon">{day.icon}</div>
              <p className="condition">{day.condition}</p>
              <div className="temp-range">
                <span className="high">{day.high}</span>
                <span className="low">{day.low}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      <div className="weather-tips">
        <h3>旅行建议</h3>
        <ul>
          {weatherData.tips.map((tip, index) => (
            <li key={index}>{tip}</li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default WeatherPage;