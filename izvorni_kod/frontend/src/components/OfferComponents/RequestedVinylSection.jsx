import React from 'react';

export const RequestedVinylSection = ({ record, onVinylClick }) => {
  return (
    <div className="requested-vinyl">
      <h4>Requested Record:</h4>
      <div 
        className="vinyl-item" 
        onClick={() => onVinylClick(record.id)}
      >
        <h3>{record.album_name}</h3>
        <p>Artist: {record.artist}</p>
      </div>
    </div>
  );
};