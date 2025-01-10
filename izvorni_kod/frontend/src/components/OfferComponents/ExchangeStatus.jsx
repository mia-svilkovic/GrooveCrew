import React from 'react';

export const ExchangeStatus = ({ exchange, userId }) => {
  const isInitiator = exchange.initiator_user.id === userId;
  const statusText = exchange.next_user_to_review.id === userId
    ? "Waiting for your review"
    : `Waiting for ${isInitiator ? 'receiver' : 'initiator'}'s review`;

  return (
    <div className={`exchange-status ${exchange.next_user_to_review.id === userId ? 'active' : 'waiting'}`}>
      <span>{statusText}</span>
    </div>
  );
};
