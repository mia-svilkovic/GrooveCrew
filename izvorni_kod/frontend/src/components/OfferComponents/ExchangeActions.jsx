import React from 'react';

export const ExchangeActions = ({
  isCurrentReviewer,
  isReceiver,
  onSubmitReview,
  onReset,
  onOpenRequestForm,
  onFinalize,
  onCancel
}) => {
  return (
    <div className="exchange-actions">
      {isCurrentReviewer && (
        <>
          <button className="review-button" onClick={onSubmitReview}>
            Submit Review
          </button>
          <button className="reset-button" onClick={onReset}>
            Reset Changes
          </button>
        </>
      )}

      {isCurrentReviewer && isReceiver && (
        <>
          <button onClick={onOpenRequestForm}>
            Request Additional Record
          </button>
          <button className="finalize-button" onClick={onFinalize}>
            Finalize Exchange
          </button>
        </>
      )}

      <button className="cancel-button" onClick={onCancel}>
        Cancel Exchange
      </button>
    </div>
  );
};