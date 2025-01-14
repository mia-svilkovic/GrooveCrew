import React, { useState } from "react";
import "./AllVinyls.css";
import exchange from "../assets/images/exchange.png";
import ExchangeForm from "./forms/ExchangeForm";
import { useNavigate } from "react-router-dom";
import { useUser } from "../contexts/UserContext";


function AllVinyls({ filteredVinyls }) {
    const navigate = useNavigate();
    const [showExchangeForm, setShowExchangeForm] = useState(false);
    const [selectedVinylId, setSelectedVinylId] = useState(null);
    const { user } = useUser();

    const handleVinylClick = (vinylId) => {
        navigate(`/vinyl/${vinylId}`);
    };

    const handleUserClick = (userId) => {
        navigate(`/user/${userId}`);
    };

    const handleExchangeClick = (e, vinylId) => {
        e.stopPropagation();
        setSelectedVinylId(vinylId);        
        setShowExchangeForm(true);
    };

    return (
        <div className="vinyls-container">
            <div className="debug-info">
                <p>results: {filteredVinyls.length}</p>
            </div>
            {filteredVinyls.length === 0 ? (
                <p>No vinyls found.</p>
            ) : (
                <div className="vinyl-list">
                    {filteredVinyls.map((vinyl) => (
                        <div
                            key={vinyl.id}
                            className="vinyl-item"
                            onClick={() => handleVinylClick(vinyl.id)}
                            style={{ cursor: 'pointer' }}
                        >
                            <h3>{vinyl.album_name}</h3>
                            <p>Artist: {vinyl.artist}</p>
                           
                            <div className="select-text">
                                <p onClick={(e) => {
                                    e.stopPropagation();
                                    handleUserClick(vinyl.user.id);
                                }}>
                                    Owner: {vinyl.user.username}
                                </p>
                            </div>
                            <div>
                            {vinyl.available_for_exchange && (!user || vinyl.user.id !== user.id) &&(
                                <button
                                    onClick={(e) => handleExchangeClick(e, vinyl.id, vinyl.user.id)}
                                    className="vinyl-opt">
                                    <img src={exchange} alt={exchange} />
                                </button>
                            )}  
                            </div>
                        </div>
                    ))}
                </div>
            )}
            {showExchangeForm &&(
                <div className="modal-overlay">
                    <ExchangeForm
                        selectedVinylId={selectedVinylId}
                        onClose={() => {
                            setShowExchangeForm(false);
                            setSelectedVinylId(null);
                        }}
                    />
                </div>
            )}
        </div>
    );
}

export default AllVinyls;