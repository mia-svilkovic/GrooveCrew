import React, { useState, useEffect } from "react";
// import "./my-vinyls.css";
import exchange from "../../assets/images/exchange.png";
import { useParams, useNavigate } from 'react-router-dom';
import "./UserDetail.css";

const URL = import.meta.env.VITE_API_URL;

function UserDetail() {

  const [vinyls, setVinyls] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");
  const { id } = useParams();
  const navigate = useNavigate();


  const handleVinylClick = (vinylId) => {
    navigate(`/vinyl/${vinylId}`);
  };

  // Fetch all vinyls when the component mounts
  useEffect(() => {
    const fetchVinyls = async () => {
      try {
        const response = await fetch(`${URL}/api/records/user/${id}`, {
          method: "GET",
          credentials: "include",
        });
        if (!response.ok) {
          throw new Error("Failed to fetch vinyls");
        }
        const data = await response.json();
        setVinyls(data);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching vinyls:", error);
        setErrorMessage("Failed to load vinyl records. Please try again.");
        setLoading(false);
      }
    };
    fetchVinyls();
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (errorMessage) {
    return <div className="error-message">{errorMessage}</div>;
  }
  return (
    <div className="user-container">
        <button 
        onClick={() => navigate(-1)}
        className="back-button"
        >
            ← Back
        </button>       
        <div className="user-header">
            <h1>{vinyls[0].user.username}</h1>
        </div>
        
        <div className="user-details">
            <p>First name: {vinyls[0].user.first_name}</p>
            <p>Last name: {vinyls[0].user.last_name}</p>
            <p>email: {vinyls[0].user.email}</p>
            <p>published records:{vinyls.length}</p>
        </div>
        <div className="vinyls-container">
            <h2>{vinyls[0].user.username}'s records: </h2>
            {vinyls.length === 0 ? (
                <p>{vinyls[0].user.username} does not have any vinyls published.</p>
            ) : (
                <div className="vinyl-list">
                    {vinyls.map((vinyl) => (
                        <div 
                        key={vinyl.id} 
                        className="vinyl-item"
                        onClick={() => handleVinylClick(vinyl.id)}
                        style={{ cursor: 'pointer' }}
                        >
                        <h3>{vinyl.album_name}</h3>
                        <p>Artist: {vinyl.artist}</p>
                        <p>Location: {vinyl.location}</p>
                        <p>
                            Available for Exchange:{" "}
                            {vinyl.available_for_exchange ? "Yes" : "No"}
                        </p>
                        <div>
                            <button onClick={(e) => e.stopPropagation()} key={vinyl.id + "exchange"} className="vinyl-opt">
                            <img src={exchange} alt={exchange} />
                            </button>
                        </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    </div>
  );
}
export default UserDetail;
