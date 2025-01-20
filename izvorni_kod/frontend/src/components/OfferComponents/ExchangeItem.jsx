import React from 'react';
import { ExchangeStatus } from './ExchangeStatus';
import { ExchangeParties } from './ExchangeParties';
import { RequestedVinylSection } from './RequestedVinylSection';
import { OfferedVinylSection } from './OfferedVinylSection';
import { AdditionalRequestedSection } from './AdditionalRequestedSection';
import { ExchangeActions } from './ExchangeActions';

export const ExchangeItem = ({
  exchange,
  currentExchange,
  userId,
  onUserClick,
  onVinylClick,
  onRemoveRecord,
  onAcceptRequest,
  onRejectRequest,
  onSubmitReview,
  onReset,
  onOpenRequestForm,
  onFinalize,
  onCancel
}) => {
  const isCurrentReviewer = exchange.next_user_to_review.id === userId;
  const isReceiver = exchange.receiver_user.id === userId;
  const isInitiator = exchange.initiator_user.id === userId;
  const hasRequestedRecords = currentExchange.records_requested_by_receiver?.length > 0;

  return (
    <div className="exchange-container">
      <ExchangeStatus exchange={exchange} userId={userId} />
      <ExchangeParties exchange={exchange} onUserClick={onUserClick} />
      
      <RequestedVinylSection 
        record={exchange.requested_record}
        onVinylClick={onVinylClick}
      />
      
      <OfferedVinylSection
        records={currentExchange.offered_records}
        onVinylClick={onVinylClick}
        onRemoveRecord={onRemoveRecord}
        showRemoveButton={isCurrentReviewer}
        exchange={exchange}
      />
      
      <AdditionalRequestedSection
        records={currentExchange.records_requested_by_receiver}
        onVinylClick={onVinylClick}
        onAccept={onAcceptRequest}
        onReject={onRejectRequest}
        showActions={isInitiator && isCurrentReviewer}
      />
      
      <ExchangeActions
        isCurrentReviewer={isCurrentReviewer}
        isReceiver={isReceiver}
        onSubmitReview={onSubmitReview}
        onReset={onReset}
        onOpenRequestForm={onOpenRequestForm}
        onFinalize={onFinalize}
        onCancel={onCancel}
        hasRequestedRecords={hasRequestedRecords}
      />
    </div>
  );
};