import React, { useState, useEffect } from "react";
import "./AllVinyls.css"; // Add your custom styles if needed
import like from "../assets/images/like.png";
import exchange from "../assets/images/exchange.png";

const URL = import.meta.env.VITE_API_URL;


function AllVinyls({ filterFunction}) {
  
  const [vinyls, setVinyls] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");


  // Fetch all vinyls when the component mounts
  useEffect(() => {
    const fetchVinyls = async () => {

      try {
        const response = await fetch(`${URL}get_records/`, {
          method: "GET",
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

  const filteredVinyls = filterFunction ? filterFunction(vinyls) : vinyls;

  if (loading) {
    return <div>Loading...</div>;
  }

  if (errorMessage) {
    return <div className="error-message">{errorMessage}</div>;
  }

 

  return (
    <div className="vinyls-container">
      <div className="debug-info" style={{ marginBottom: '20px', color: '#666' }}>
        <p>Total vinyls: {vinyls.length}</p>
        <p>Filtered vinyls: {filteredVinyls.length}</p>
      </div>
      {filteredVinyls.length === 0 ? (
        <p>No vinyls found.</p>
      ) : (
        <div className="vinyl-list">
          {filteredVinyls.map((vinyl) => (
            <div key={vinyl.id} className="vinyl-item">

                <h3>{vinyl.album_name}</h3>
                  <p>Artist: {vinyl.artist}</p>
                  <p>Genre: {vinyl.genre}</p>
                  {/* <p>Location: {vinyl.location.city}, {vinyl.location.country}</p> */}
                  <p>Available for Exchange: {vinyl.available_for_exchange ? "Yes" : "No"}</p>
                  <p>Description: {vinyl.additional_description}</p>
                  <div>
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
