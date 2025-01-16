import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../../contexts/UserContext';
import { useAuthRefresh } from '../../contexts/AuthRefresh';
import { ExchangeItem } from '../OfferComponents/ExchangeItem';
import RequestRecordForm from '../forms/RequestRecordForm';
import './Offers.css';

const URL = import.meta.env.VITE_API_URL;

function Offers({ onNeedRefresh }) {
  const [exchanges, setExchanges] = useState([]);
  const [modifiedExchanges, setModifiedExchanges] = useState({});
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [showRequestForm, setShowRequestForm] = useState(false);
  const [selectedExchangeId, setSelectedExchangeId] = useState(null);

  const { user } = useUser();
  const { authFetch } = useAuthRefresh();
  const navigate = useNavigate();

  useEffect(() => {
    if (!user) navigate("/");
    fetchExchanges();
  }, []);

  useEffect(() => {
    if (successMessage) setTimeout(() => setSuccessMessage(""), 5000);
    if (errorMessage) setTimeout(() => setErrorMessage(""), 5000);
  }, [successMessage, errorMessage]);

  const fetchExchanges = async () => {
    try {
      const response = await authFetch(`${URL}/api/exchanges/`);
      if (!response.ok) throw new Error("Failed to fetch exchanges");
      const data = await response.json();
      setExchanges(data);
      setLoading(false);
    } catch (error) {
      setErrorMessage("Failed to load exchanges");
      setLoading(false);
    }
  };

  const handleVinylClick = (vinylId) => {
    navigate(`/vinyl/${vinylId}`);
  };

  const handleOpenRequestForm = (exchangeId) => {
    setSelectedExchangeId(exchangeId);
    setShowRequestForm(true);
  };

  const handleRequestFormSuccess = (selectedRecords) => {
    const exchange = exchanges.find(e => e.id === selectedExchangeId);
    const currentModifiedExchange = modifiedExchanges[selectedExchangeId] || exchange;
    
    const updatedRequestedRecords = [
      ...(currentModifiedExchange.records_requested_by_receiver || []),
      ...selectedRecords
    ];

    setModifiedExchanges(prev => ({
      ...prev,
      [selectedExchangeId]: {
        ...currentModifiedExchange,
        records_requested_by_receiver: updatedRequestedRecords
      }
    }));
    setSuccessMessage("Records selected successfully!");
    setShowRequestForm(false);
  };

  const handleUpdateExchange = async (exchangeId) => {
    const exchange = exchanges.find(e => e.id === exchangeId);
    const modifiedExchange = modifiedExchanges[exchangeId] || exchange;

    //if (!validateExchange(exchange, modifiedExchange)) return false;

    try {
      const updateResponse = await authFetch(`${URL}/api/exchanges/${exchangeId}/update/`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          offered_records: modifiedExchange.offered_records.map(record => ({
            record_id: record.record.id
          })),
          records_requested_by_receiver: modifiedExchange.records_requested_by_receiver.map(record => ({
            record_id: record.record.id
          }))
        })
      });

      if (!updateResponse.ok) {
        const error = await updateResponse.json();
        throw new Error(error.message || "Failed to update exchange");
        //onNeedRefresh() ;
      }

      return true;
    } catch (error) {
      setErrorMessage(error.message);
      return false;
    }
  };

  const handleFinalize = async (exchangeId) => {
    try {
      setLoading(true);
      
      const updateSuccess = await handleUpdateExchange(exchangeId);
      if (!updateSuccess) return;

      const finalizeResponse = await authFetch(`${URL}/api/exchanges/${exchangeId}/finalize/`, {
        method: "POST",
      });
      
      if (!finalizeResponse.ok) {
        const error = await finalizeResponse.json();
        throw new Error(error.message || "Failed to finalize exchange");
      }

      setSuccessMessage("Exchange finalized successfully!");
      onNeedRefresh();
    } catch (error) {
      setErrorMessage(error.message);
      onNeedRefresh();
    } finally {
      setLoading(false);
      onNeedRefresh();
    }
  };

  const handleCancel = async (exchangeId) => {
    try {
      const response = await authFetch(`${URL}/api/exchanges/${exchangeId}/delete/`, {
        method: "DELETE",
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || "Failed to cancel exchange");
      }

      setSuccessMessage("Exchange cancelled successfully!");
      onNeedRefresh();
    } catch (error) {
      setErrorMessage(error.message);
    }
  };

  const handleRemoveRecord = (exchangeId, recordId) => {
    const exchange = exchanges.find(e => e.id === exchangeId);
    const currentModifiedExchange = modifiedExchanges[exchangeId] || exchange;
    const updatedRecords = currentModifiedExchange.offered_records.filter(
      record => record.record.id !== recordId
    );
    
    setModifiedExchanges(prev => ({
      ...prev,
      [exchangeId]: {
        ...currentModifiedExchange,
        offered_records: updatedRecords
      }
    }));
  };

  const handleAddToOffered = (exchangeId, recordId) => {
    const exchange = exchanges.find(e => e.id === exchangeId);
    const currentModifiedExchange = modifiedExchanges[exchangeId] || exchange;
    
    const recordToAdd = currentModifiedExchange.records_requested_by_receiver
      .find(r => r.id === recordId || r.record.id === recordId);
    if (!recordToAdd) return;

    const updatedOfferedRecords = [
      ...currentModifiedExchange.offered_records,
      recordToAdd
    ];
    const updatedExchange = {
      ...currentModifiedExchange,
      records_requested_by_receiver: currentModifiedExchange.records_requested_by_receiver
        .filter(r => r.id !== recordId && r.record.id !== recordId),
      offered_records: updatedOfferedRecords
    };

    setModifiedExchanges(prev => ({
      ...prev,
      [exchangeId]: updatedExchange
    }));
  };

  const handleRejectRequested = (exchangeId, recordId) => {
    const exchange = exchanges.find(e => e.id === exchangeId);
    const currentModifiedExchange = modifiedExchanges[exchangeId] || exchange;
    const updatedExchange = {
      ...currentModifiedExchange,
      records_requested_by_receiver: currentModifiedExchange.records_requested_by_receiver
        .filter(r => r.id !== recordId && r.record.id !== recordId)
    };
    setModifiedExchanges(prev => ({
      ...prev,
      [exchangeId]: updatedExchange
    }));
  };

  const handleReset = (exchangeId) => {
    setModifiedExchanges(prev => {
      const newState = { ...prev };
      delete newState[exchangeId];
      return newState;
    });
  };

  const validateExchange = (exchange, modifiedExchange) => {
    if (exchange.receiver_user.id === user.id && 
        (!modifiedExchange.records_requested_by_receiver?.length)) {
      setErrorMessage("Please request at least one record");
      return false;
    }
    if (exchange.initiator_user.id === user.id && 
      (modifiedExchange.records_requested_by_receiver?.length)) {
      setErrorMessage("Please accept or reject all requested records");
      return false;
    }    
    return true;
  };

  const handleSubmitReview = async (exchangeId) => {
    try {
      setLoading(true);
      const exchange = exchanges.find(e => e.id === exchangeId);
      const modifiedExchange = modifiedExchanges[exchangeId] || exchange;

      if (!validateExchange(exchange, modifiedExchange)) return false;

      const updateSuccess = await handleUpdateExchange(exchangeId);
      if (!updateSuccess) onNeedRefresh();

      const switchResponse = await authFetch(`${URL}/api/exchanges/${exchangeId}/switch-reviewer/`, {
        method: "POST"
      });
      
      if (!switchResponse.ok) {
        const error = await switchResponse.json();
        throw new Error(error.message || "Failed to switch reviewer");
      }

      setSuccessMessage("Review submitted successfully");
      onNeedRefresh();
    } catch (error) {
      setErrorMessage(error.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (!user) return null;

  return (
    <div className="vinyls-container">
      <h2>My Exchanges</h2>
      {successMessage && <div className="success-message">{successMessage}</div>}
      {errorMessage && <div className="error-message">{errorMessage}</div>}

      <div className="exchange-list">
        {exchanges.filter(exchange => !exchange.completed).length === 0 ? (
          <p>You don't have any active exchanges in progress.</p>
        ) : (
          exchanges
            .filter(exchange => !exchange.completed)
            .map(exchange => (
              <ExchangeItem
                key={exchange.id}
                exchange={exchange}
                currentExchange={modifiedExchanges[exchange.id] || exchange}
                userId={user.id}
                onUserClick={(userId) => navigate(`/user/${userId}`)}
                onVinylClick={handleVinylClick}
                onRemoveRecord={(exchangeId, recordId) => handleRemoveRecord(exchange.id, recordId)}
                onAcceptRequest={(recordId) => handleAddToOffered(exchange.id, recordId)}
                onRejectRequest={(recordId) => handleRejectRequested(exchange.id, recordId)}
                onSubmitReview={() => handleSubmitReview(exchange.id)}
                onReset={() => handleReset(exchange.id)}
                onOpenRequestForm={() => handleOpenRequestForm(exchange.id)}
                onFinalize={() => handleFinalize(exchange.id)}
                onCancel={() => handleCancel(exchange.id)}
              />
            ))
        )}
      </div>

      {showRequestForm && (
        <div className="modal-overlay">
          <RequestRecordForm
            exchange={modifiedExchanges[selectedExchangeId] || 
              exchanges.find(e => e.id === selectedExchangeId)}
            onClose={() => setShowRequestForm(false)}
            onSuccess={handleRequestFormSuccess}
          />
        </div>
      )}
    </div>
  );
}

export default Offers;