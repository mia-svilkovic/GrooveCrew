import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useUser } from "../../contexts/UserContext";
import { useAuthRefresh } from "../../contexts/AuthRefresh";
import { ExchangeParties } from '../OfferComponents/ExchangeParties';
import { RequestedVinylSection } from '../OfferComponents/RequestedVinylSection';
import { OfferedVinylSection } from '../OfferComponents/OfferedVinylSection';

const URL = import.meta.env.VITE_API_URL;

const History = () => {
    const [exchanges, setExchanges] = useState([]);
    const [loading, setLoading] = useState(true);
    const [errorMessage, setErrorMessage] = useState("");

    const { user } = useUser();
    const { authFetch } = useAuthRefresh();
    const navigate = useNavigate();

    useEffect(() => {
        if (!user) navigate("/");
        fetchExchanges();
    }, []);

    const fetchExchanges = async () => {
        try {
        const response = await authFetch(`${URL}/api/exchanges/`);
        if (!response.ok) throw new Error("Failed to fetch exchanges");
        const data = await response.json();
        setExchanges(data.filter(exchange => exchange.completed));
        setLoading(false);
        } catch (error) {
        setErrorMessage("Failed to load exchanges");
        setLoading(false);
        }
    };

    const handleVinylClick = (vinylId) => {
        navigate(`/vinyl/${vinylId}`);
    };

    if (loading) return <div>Loading...</div>;
    if (!user) return null;

    return (
        <div className="vinyls-container">
        <h2>Exchange History</h2>
        {errorMessage && <div className="error-message">{errorMessage}</div>}

        <div className="exchange-list">
            {exchanges.length === 0 ? (
            <p>You don't have any completed exchanges.</p>
            ) : (
            exchanges.map(exchange => (
                <div key={exchange.id} className="exchange-container">
                <div className="exchange-header">
                    <span className="exchange-date">
                    Completed on: {new Date(exchange.last_modification_datetime).toLocaleDateString()}
                    </span>
                    
                    <ExchangeParties exchange={exchange} 
                    onUserClick={() => navigate(`/user/${exchange.receiver_user.id}`)}  />
                </div>

                <RequestedVinylSection 
                    record={exchange.requested_record}
                    onVinylClick={handleVinylClick}
                />

                <div className="offered-vinyl">
                    <h4>Exchanged Records:</h4>
                    {exchange.offered_records.map(record => (
                    <div
                        key={record.id}
                        className="vinyl-item"
                        onClick={() => handleVinylClick(record.record.id)}
                    >
                        <h3>{record.record.album_name}</h3>
                        <p>Artist: {record.record.artist}</p>
                    </div>
                    ))}
                </div>
            
            </div>
            ))
            )}
        </div>
        </div>
    );
    };

    export default History;