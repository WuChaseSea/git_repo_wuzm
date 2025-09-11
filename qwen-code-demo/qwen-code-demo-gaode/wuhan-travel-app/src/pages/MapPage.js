import React, { useEffect } from 'react';
import './MapPage.css';

const MapPage = () => {
  useEffect(() => {
    // Dynamically load the AMap script
    const script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = 'https://webapi.amap.com/maps?v=1.4.15&key=YOUR_AMAP_KEY_HERE';
    script.async = true;
    script.onload = () => {
      // Initialize the map after the script is loaded
      initMap();
    };
    document.head.appendChild(script);

    return () => {
      // Clean up the script when the component unmounts
      document.head.removeChild(script);
    };
  }, []);

  const initMap = () => {
    // Initialize the map centered on Wuhan
    const map = new window.AMap.Map('map-container', {
      zoom: 11,
      center: [114.3052, 30.5929], // Wuhan coordinates
      mapStyle: 'amap://styles/normal'
    });

    // Add markers for key attractions
    const attractions = [
      { name: '黄鹤楼', position: [114.2990, 30.5509] },
      { name: '武汉大学', position: [114.4117, 30.5485] },
      { name: '东湖风景区', position: [114.4117, 30.5485] },
      { name: '户部巷', position: [114.2951, 30.5533] },
      { name: '长江大桥', position: [114.2940, 30.5520] }
    ];

    attractions.forEach(attraction => {
      const marker = new window.AMap.Marker({
        position: attraction.position,
        title: attraction.name,
        map: map
      });

      // Add info window for each marker
      const infoWindow = new window.AMap.InfoWindow({
        content: `<div><strong>${attraction.name}</strong><p>热门景点</p></div>`,
        offset: new window.AMap.Pixel(0, -30)
      });

      marker.on('click', () => {
        infoWindow.open(map, marker.getPosition());
      });
    });

    // Add a scale control
    map.addControl(new window.AMap.Scale());

    // Add a toolbar control
    map.addControl(new window.AMap.ToolBar());
  };

  return (
    <div className="map-page">
      <h2>武汉旅游地图</h2>
      <p>点击标记查看景点详情</p>
      <div id="map-container" className="map-container"></div>
    </div>
  );
};

export default MapPage;