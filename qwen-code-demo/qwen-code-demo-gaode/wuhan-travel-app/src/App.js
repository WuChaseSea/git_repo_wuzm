import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ItineraryPage from './pages/ItineraryPage';
import MapPage from './pages/MapPage';
import WeatherPage from './pages/WeatherPage';
import Navigation from './components/Navigation';
import Footer from './components/Footer';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <header className="app-header">
          <h1>武汉浪漫之旅</h1>
          <p>四天三夜情侣旅行攻略</p>
        </header>
        <Navigation />
        <main>
          <Routes>
            <Route path="/" element={<ItineraryPage />} />
            <Route path="/map" element={<MapPage />} />
            <Route path="/weather" element={<WeatherPage />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
}

export default App;