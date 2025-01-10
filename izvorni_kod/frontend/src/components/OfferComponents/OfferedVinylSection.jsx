import React from 'react';

export const OfferedVinylSection = ({ records, onVinylClick, onRemoveRecord, showRemoveButton }) => {
  return (
    <div className="offered-vinyl">
      <h4>Offered Records:</h4>
      {records.map(record => (
        <div key={record.id} className="vinyl-item">
          <div onClick={() => onVinylClick(record.record.id)}>
            <h3>{record.record.album_name}</h3>
            <p>Artist: {record.record.artist}</p>
          </div>
          {showRemoveButton && (
            <button onClick={(e) => {
              e.stopPropagation();
              onRemoveRecord(record.record.id);
            }}>
              Remove
            </button>
          )}
        </div>
      ))}
    </div>
  );
};