import React, { useState, useEffect } from 'react';
import './Form.css';
// import './exchange.css';
import { useNavigate } from "react-router-dom";
import { useUser } from "../../contexts/UserContext";
import FormLogin from './FormLogin';
import { useAuthRefresh } from '../../contexts/AuthRefresh';



const URL = import.meta.env.VITE_API_URL;

function ExchangeForm({ selectedVinylId, onClose }) {
    const navigate = useNavigate();
    const [userVinyls, setUserVinyls] = useState([]);
    const [selectedVinylsForExchange, setSelectedVinylsForExchange] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [successMessage, setSuccessMessage] = useState("");
    const [errorMessage, setErrorMessage] = useState("");
    const [showLoginForm, setShowLoginForm] = useState(false);

    const { user } = useUser();
    const { authFetch } = useAuthRefresh();
    
    if (!user?.username) {
        return <FormLogin onClose={() => {
            setShowLoginForm(false);
            onClose();
        }} showMessage={true}/>;
    }

    const userId = user.id;

    useEffect(() => {
        if (successMessage) {
          const timer = setTimeout(() => {
            setSuccessMessage("");
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
            const response = await authFetch(`${URL}/api/records/user/${userId}`, {
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
        setSelectedVinylsForExchange(prev => {
            if (prev.includes(vinylId)) {
                return prev.filter(id => id !== vinylId);
            }
            return [...prev, vinylId];
        });
    };
    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!selectedVinylsForExchange.length) {
            setErrorMessage('Please select at least one vinyl for exchange');
            return;
        }
        try {
            const token = localStorage.getItem("access");
            const response = await fetch(`${URL}/api/records/exchange/${selectedVinylId}`, {
                method: 'POST',
                headers: {
                    Authorization: token ? `Bearer ${token}` : "",
                },
                body: JSON.stringify({
                    vinyls: selectedVinylsForExchange
                }),
                credentials: "include"
            });
            if (!response.ok) {
                setErrorMessage('Failed to submit exchange request');
                throw new Error('Failed to submit exchange request');
                
            }
            setSuccessMessage('Exchange request submitted successfully!');
            onClose();
        } catch (error) {
            console.error('Error submitting exchange:', error);
            setErrorMessage('Failed to submit exchange request. Please try again.');
        }
        
    };

    if (loading) return <div className="form-container">Loading...</div>;
    if (error) return <div className="form-container">{error}</div>;

    if (userVinyls.length === 0) {
        return (
            <div className="form-container">
                
                    <h3>No Vinyls Available :( </h3>
                    <p className='note'>You have no published vinyls.Publish a vinyl to offer exchange.</p>
                    <button className='close-button' type="button" onClick={onClose}>
                        OK
                    </button>
                
            </div>
        );
    }

    return (
        <div className="form-container" id='plus-container'>
            <div className="exchange-form">
                <h3>Select Vinyls for Exchange</h3>
                <form onSubmit={handleSubmit}>
                    <div className="check-options">
                        {userVinyls.map(vinyl => (
                            <label key={vinyl.id} className="check-option">
                                <input
                                    type="checkbox"
                                    checked={selectedVinylsForExchange.includes(vinyl.id)}
                                    onChange={() => handleVinylSelection(vinyl.id)}
                                />
                                <div className="select-text">
                                    <p onClick={() => handleVinylClick(vinyl.id)}>
                                        {vinyl.album_name} ({vinyl.catalog_number})
                                    </p>
                                </div>
                            </label>
                        ))}
                    </div>

                    {successMessage && <p className="success-message">{successMessage}</p>}
                    {errorMessage && <p className="error-message">{errorMessage}</p>}        
                    <button type="submit">Submit Exchange</button>
                    <button className='closFailed to load vinyl records. Please try again.e-button' type="button" onClick={onClose}>
                        Cancel
                    </button>

                </form>
            </div>
        </div>
    );
}

export default ExchangeForm ;