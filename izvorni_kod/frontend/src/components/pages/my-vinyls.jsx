import React, { useState, useEffect } from "react";
// import "./my-vinyls.css";
import bin from "../../assets/images/bin.png";
import edit from "../../assets/images/edit.png";
import { useUser } from "../../contexts/UserContext";
import { useNavigate } from "react-router-dom";


const URL = import.meta.env.VITE_API_URL;

function MyVinyls() {
  const [vinyls, setVinyls] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  const { user } = useUser();
  const userId = user.id;

  const navigate = useNavigate();
  const handleVinylClick = (vinylId) => {
    navigate(`/vinyl/${vinylId}`);
  };
  const handleUserClick = (userId) => {
    navigate(`/user/${userId}`);
  };

  // Fetch all vinyls when the component mounts
  useEffect(() => {
    const fetchVinyls = async () => {
      try {
        const response = await fetch(`${URL}/api/records/user/${userId}`, {
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
    <div className="vinyls-container">
      <h2>My Vinyl Records</h2>
      {vinyls.length === 0 ? (
        <p>You don't have any vinyls published.</p>
      ) : (
        <div className="vinyl-list">
          {vinyls.map((vinyl) => (
            <div key={vinyl.id} className="vinyl-item"
            onClick={() => handleVinylClick(vinyl.id)}
            style={{ cursor: 'pointer' }}
            >
              <h3>{vinyl.album_name}</h3>
              <p>Artist: {vinyl.artist}</p>
              <p>Genre: {vinyl.genre.name}</p>
              <p>Location: {vinyl.location}</p>
              <p>
                Available for Exchange:{" "}
                {vinyl.available_for_exchange ? "Yes" : "No"}
              </p>
              <p>Description: {vinyl.additional_description}</p>
              <div>
                <button key={vinyl.id + "edit"} className="vinyl-opt">
                  <img src={edit} alt={edit} />
                </button>
                <button key={vinyl.id + "delete"} className="vinyl-opt">
                  <img src={bin} alt={bin} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
export default MyVinyls;
