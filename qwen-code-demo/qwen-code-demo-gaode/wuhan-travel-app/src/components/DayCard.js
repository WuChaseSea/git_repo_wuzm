import React from 'react';
import './DayCard.css';

const DayCard = ({ time, name, description, image }) => {
  return (
    <div className="day-card">
      <div className="time-badge">{time}</div>
      <img src={image} alt={name} />
      <div className="card-content">
        <h3>{name}</h3>
        <p>{description}</p>
      </div>
    </div>
  );
};

export default DayCard;