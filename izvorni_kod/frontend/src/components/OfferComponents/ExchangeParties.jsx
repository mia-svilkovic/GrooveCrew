import React from 'react';

export const ExchangeParties = ({ exchange, onUserClick }) => {
  return (
    <div className="exchange-parties">
      <div className="party initiator">
        <span 
          className="select-text"
          onClick={(e) => {
            e.stopPropagation();
            onUserClick(exchange.initiator_user.id);
          }}
        >
          <strong>Initiator:</strong> {exchange.initiator_user.username}
        </span>
      </div>
      <div className="party receiver">
        <span 
          className="select-text"
          onClick={(e) => {
            e.stopPropagation();
            onUserClick(exchange.receiver_user.id);
          }}
        >
          <strong>Receiver:</strong> {exchange.receiver_user.username}
        </span>
      </div>
    </div>
  );
};