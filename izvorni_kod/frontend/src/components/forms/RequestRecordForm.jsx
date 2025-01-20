import React, { useState, useEffect } from 'react';
import { useNavigate } from "react-router-dom";
import { useAuthRefresh } from "../../contexts/AuthRefresh";
import './Form.css';

const URL = import.meta.env.VITE_API_URL;

function RequestRecordForm({ exchange, onClose, onSuccess}) {
    const navigate = useNavigate();
    const [userVinyls, setUserVinyls] = useState([]);
    const [selectedVinylsForRequest, setSelectedVinylsForRequest] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [successMessage, setSuccessMessage] = useState("");
    const [errorMessage, setErrorMessage] = useState("");

    const { authFetch } = useAuthRefresh();
    console.log(exchange) ;
    const initiatorId = exchange.initiator_user.id ;

    useEffect(() => {
        if (successMessage) {
            const timer = setTimeout(() => {
                setSuccessMessage("");
                onSuccess();
                onClose();
            }, 2000);
            return () => clearTimeout(timer);
        }
        if (errorMessage) {
            const timer = setTimeout(() => setErrorMessage(""), 5000);
            return () => clearTimeout(timer);
        }
    }, [successMessage, errorMessage]);

    useEffect(() => {
        const fetchVinyls = async () => {
            try {
                const response = await authFetch(`${URL}/api/records/user/${initiatorId}`, {
                    method: "GET",
                });
                if (!response.ok) {
                    throw new Error("Failed to fetch vinyls");
                }
                const data = await response.json();
                
                setUserVinyls(data);
                setLoading(false);
            } catch (error) {
                console.error("Error fetching vinyls:", error);
                setErrorMessage("Failed to load vinyl records. Please try again.");
                setLoading(false);
            }
        };
        fetchVinyls();
    }, []);

    const handleVinylClick = (vinylId) => {
        navigate(`/vinyl/${vinylId}`);
    };

    const handleVinylSelection = (vinylId) => {
        setSelectedVinylsForRequest(prev => {
            if (prev.includes(vinylId)) {
                return prev.filter(id => id !== vinylId);
            }
            return [...prev, vinylId];
        });
    };
    const isVinylRequested = (vinylId) => {
        console.log(vinylId) ;
        console.log(exchange.records_requested_by_receiver) ;
        console.log(selectedVinylsForRequest) ;
        return exchange.records_requested_by_receiver.some(record => record.record.id === vinylId);
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!selectedVinylsForRequest.length) {
            setErrorMessage('Please select at least one vinyl to request');
            return;
        }
        const data = selectedVinylsForRequest.map(vinylId => {
            const record = userVinyls.find(vinyl => vinyl.id === vinylId);
            return {
                id: `temp_${vinylId}`,
                record: record
            };
        });
        onSuccess(data);
        onClose();
    };

    if (loading) return <div className="form-container">Loading...</div>;
    if (error) return <div className="form-container">{error}</div>;

    if (userVinyls.length === 0) {
        return (
            <div className="form-container">
                <h3>No Vinyls Available</h3>
                <p className='note'>There are no vinyls available to request.</p>
                <button className='close-button' type="button" onClick={onClose}>
                    OK
                </button>
            </div>
        );
    }

    return (
        <div className="form-container" id='plus-container'>
            <div className="exchange-form">
                <h3>Select Vinyls to Request</h3>
                <form onSubmit={handleSubmit}>
                    <div className="check-options">
                        {userVinyls.map(vinyl => (
                            vinyl.available_for_exchange ? (
                                isVinylRequested(vinyl.id) ? (
                                    <label key={vinyl.id} className="check-option">
                                    <div className="select-text">
                                        <span onClick={() => handleVinylClick(vinyl.id)}>
                                            {vinyl.album_name} ({vinyl.catalog_number})
                                        </span>
                                        <span className="note">[already requested]</span>
                                    </div>
                                </label>
                                ):(
                                <label key={vinyl.id} className="check-option">
                                    <input
                                        className="vinyl-checkbox"
                                        type="checkbox"
                                        checked={selectedVinylsForRequest.includes(vinyl.id)}
                                        onChange={() => handleVinylSelection(vinyl.id)}
                                    />
                                    <div className="select-text">
                                        <p onClick={() => handleVinylClick(vinyl.id)}>
                                            {vinyl.album_name} ({vinyl.catalog_number})
                                        </p>
                                    </div>
                                </label>
                                )
                            ):(
                                <div key={vinyl.id} className="check-option">
                                    <div className="select-text">
                                        <span onClick={() => handleVinylClick(vinyl.id)}>
                                            {vinyl.album_name} ({vinyl.catalog_number})
                                        </span>
                                        <span className="note">[Currently not available]</span>
                                    </div>
                                </div>
                            )
                        ))}
                    </div>

                    {successMessage && <p className="success-message">{successMessage}</p>}
                    {errorMessage && <p className="error-message">{errorMessage}</p>}
                    
                    <button type="submit">Submit Request</button>
                    <button className='close-button' type="button" onClick={onClose}>
                        Cancel
                    </button>
                </form>
            </div>
        </div>
    );
}

export default RequestRecordForm;