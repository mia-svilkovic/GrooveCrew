import React from 'react';

export const OfferedVinylSection = ({ records, onVinylClick, onRemoveRecord, showRemoveButton, exchange }) => {
  return (
    <div className="offered-vinyl">
      <h4>Offered Records:</h4>
      {records.map(record => (
        <div key={record.record.id} className="vinyl-item">
          <div onClick={() => onVinylClick(record.record.id)}>
            <h3>{record.record.album_name}</h3>
            <p>Artist: {record.record.artist}</p>
          </div>
          {showRemoveButton && (
            <button onClick={(e) => {
              e.stopPropagation();
              onRemoveRecord(exchange,record.record.id);
            }}>
              Remove
            </button>
          )}
        </div>
      ))}
    </div>
  );
};