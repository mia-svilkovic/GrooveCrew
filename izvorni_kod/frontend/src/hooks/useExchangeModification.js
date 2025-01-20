import { useState } from 'react';

export const useExchangeModification = (setErrorMessage) => {
  const [modifiedExchanges, setModifiedExchanges] = useState({});

  const handleRemoveRecord = (exchange, exchangeId, recordId, userId) => {
    const currentModifiedExchange = modifiedExchanges[exchangeId] || exchange;
    
    const updatedRecords = currentModifiedExchange.offered_records.filter(
      record => record.record.id !== recordId && record.id !== recordId
    );
  
    if (updatedRecords.length === 0 && exchange.initiator_user.id === userId) {
      setErrorMessage("At least one record must remain offered");
      return;
    }
    
    setModifiedExchanges(prev => ({
      ...prev,
      [exchangeId]: {
        ...currentModifiedExchange,
        offered_records: updatedRecords
      }
    }));
  };

  const handleAddToOffered = (exchange, exchangeId, recordId) => {
    const currentModifiedExchange = modifiedExchanges[exchangeId] || exchange;
    
    const recordToAdd = currentModifiedExchange.records_requested_by_receiver
      .find(r => r.id === recordId || r.record.id === recordId);

    if (!recordToAdd) return;

    const updatedExchange = {
      ...currentModifiedExchange,
      records_requested_by_receiver: currentModifiedExchange.records_requested_by_receiver
        .filter(r => r.id !== recordId && r.record.id !== recordId),
      offered_records: [...currentModifiedExchange.offered_records, recordToAdd]
    };

    setModifiedExchanges(prev => ({
      ...prev,
      [exchangeId]: updatedExchange
    }));
  };

  const handleRejectRequested = (exchange, exchangeId, recordId) => {
    const currentModifiedExchange = modifiedExchanges[exchangeId] || exchange;

    setModifiedExchanges(prev => ({
      ...prev,
      [exchangeId]: {
        ...currentModifiedExchange,
        records_requested_by_receiver: currentModifiedExchange.records_requested_by_receiver
          .filter(r => r.id !== recordId && r.record.id !== recordId)
      }
    }));
  };

  const handleReset = (exchangeId) => {
    setModifiedExchanges(prev => {
      const newState = { ...prev };
      delete newState[exchangeId];
      return newState;
    });
  };

  return {
    modifiedExchanges,
    setModifiedExchanges,
    handleRemoveRecord,
    handleAddToOffered,
    handleRejectRequested,
    handleReset
  };
};