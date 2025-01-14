import React from 'react';

export const ExchangeActions = ({
  isCurrentReviewer,
  isReceiver,
  onSubmitReview,
  onReset,
  onOpenRequestForm,
  onFinalize,
  onCancel,
  hasRequestedRecords
}) => {
  return (
    <div className="exchange-actions">
      {isCurrentReviewer && !isReceiver && !hasRequestedRecords && (
        <button className="review-button" onClick={onSubmitReview}>
          Submit Review
        </button>
      )}

      {isCurrentReviewer && isReceiver && (
        <>
          <button onClick={onOpenRequestForm}>
            Request Additional Record
          </button>
          {hasRequestedRecords ? (
            <>
            <button className="reset-button" onClick={onReset}>
              Reset Changes
            </button>
            <button className="review-button" onClick={onSubmitReview}>
              Submit Review
            </button>
            </>
          ) : (
            <button className="finalize-button" onClick={onFinalize}>
              Finalize Exchange
            </button>
          )}
        </>
      )}

      <button className="cancel-button" onClick={onCancel}>
        Cancel Exchange
      </button>
    </div>
  );
};