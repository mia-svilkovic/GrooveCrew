import React from 'react';

export const AdditionalRequestedSection = ({ 
  records, 
  onVinylClick, 
  onAccept, 
  onReject, 
  showActions 
}) => {
  if (!records?.length) return null;

  return (
    <div className="requested-vinyl">
      <h4>Additionally Requested Records:</h4>
      {records.map(record => (
        <div key={record.id} className="vinyl-item">
          <div onClick={() => onVinylClick(record.record.id)}>
            <h3>{record.record.album_name}</h3>
            <p>Artist: {record.record.artist}</p>
          </div>
          {showActions && (
            <div className="record-decision-buttons">
              <button className="accept-vinyl-button" onClick={() => onAccept(record.id)}>Accept</button>
              <button className="reject-vinyl-button" onClick={() => onReject(record.id)}>Reject</button>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};
