import React from "react";
import "./AllVinyls.css";
import like from "../assets/images/like.png";
import exchange from "../assets/images/exchange.png";
import { useNavigate } from "react-router-dom";

const URL = import.meta.env.VITE_API_URL;

function AllVinyls({filteredVinyls}) {
  const navigate = useNavigate();

  const handleVinylClick = (vinylId) => {
    navigate(`/vinyl/${vinylId}`);
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
              <p>Location: {vinyl.location}</p>
              <p>
                Available for Exchange:{" "}
                {vinyl.available_for_exchange ? "Yes" : "No"}
              </p>
              <p>Owner: {vinyl.user.username}</p>
              <div onClick={(e) => e.stopPropagation()}>
                <button key={vinyl.id + "exchange"} className="vinyl-opt">
                  <img src={exchange} alt={exchange} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default AllVinyls;