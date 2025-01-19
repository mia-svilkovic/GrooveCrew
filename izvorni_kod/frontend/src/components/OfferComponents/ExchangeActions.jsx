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
          <button onClick={onOpenRequestForm} className="additional-request-button">
            Request Additional Record
          </button>
          <button className="reset-button" onClick={onReset}>
              Reset Changes
          </button>
          {hasRequestedRecords ? (
            <>
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