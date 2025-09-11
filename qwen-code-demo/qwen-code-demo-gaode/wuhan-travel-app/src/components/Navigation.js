import React from 'react';
import { Link } from 'react-router-dom';
import './Navigation.css';

const Navigation = () => {
  return (
    <nav className="navigation">
      <ul>
        <li>
          <Link to="/">行程规划</Link>
        </li>
        <li>
          <Link to="/map">地图导航</Link>
        </li>
        <li>
          <Link to="/weather">天气预报</Link>
        </li>
      </ul>
    </nav>
  );
};

export default Navigation;