import React, { useState, useEffect } from "react";
import bin from "../../assets/images/bin.png";
import edit from "../../assets/images/edit.png";
import { useUser } from "../../contexts/UserContext";
import { useNavigate } from "react-router-dom";
import DeleteForm from "../forms/DeleteForm";
import EditForm from "../forms/EditForm";
import { useAuthRefresh } from '../../contexts/AuthRefresh';

const URL = import.meta.env.VITE_API_URL;

function MyVinyls() {
  const [vinyls, setVinyls] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");
  const [activeForm, setActiveForm] = useState(null);
  const [selectedVinyl, setSelectedVinyl] = useState(null);

  const { user } = useUser();
  const { authFetch } = useAuthRefresh();
  const navigate = useNavigate();

  const handleVinylClick = (vinylId) => {
    navigate(`/vinyl/${vinylId}`);
  };

  const handleEdit = (e, vinyl) => {
    e.stopPropagation();
    setSelectedVinyl(vinyl);
    setActiveForm('edit');
    console.log(vinyl) ;
  };

  const handleDelete = (e, vinyl) => {
    e.stopPropagation();
    setSelectedVinyl(vinyl);
    setActiveForm('delete');
  };

  const closeForm = () => {
    setActiveForm(null);
    setSelectedVinyl(null);
  };

  const handleVinylUpdate = (updatedVinyl) => {
    setVinyls(vinyls.map(v => v.id === updatedVinyl.id ? updatedVinyl : v));
    closeForm();
    console.log(updatedVinyl) ;
  };

  const handleVinylDelete = (deletedVinylId) => {
    setVinyls(vinyls.filter(v => v.id !== deletedVinylId));
    closeForm();
  };

  useEffect(() => {
    const fetchVinyls = async () => {
      try {
        const { user } = useUser();
        const response = await authFetch(`${URL}/api/records/user/${user.id}`, {
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

  if (loading) return <div>Loading...</div>;
  if (errorMessage) return <div className="error-message">{errorMessage}</div>;

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
              style={{ cursor: 'pointer' }}>
              <h3>{vinyl.album_name}</h3>
              <p>Artist: {vinyl.artist}</p>
              <p>Genre: {vinyl.genre.name}</p>
              
              <p>Available for Exchange: {vinyl.available_for_exchange ? "Yes" : "No"}</p>
              <div>
                <button onClick={(e) => handleEdit(e, vinyl)} className="vinyl-opt">
                  <img src={edit} alt="edit" />
                </button>
                <button onClick={(e) => handleDelete(e, vinyl)} className="vinyl-opt">
                  <img src={bin} alt="delete" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {activeForm === 'edit' && selectedVinyl && (
        <div className="modal-overlay">
          <EditForm
            vinyl={selectedVinyl}
            onClose={closeForm}
            onUpdate={handleVinylUpdate}
          />
        </div>
      )}

      {activeForm === 'delete' && selectedVinyl && (
        <div className="modal-overlay">
          <DeleteForm
            vinyl={selectedVinyl}
            onClose={closeForm}
            onDelete={handleVinylDelete}
          />
        </div>
      )}
    </div>
  );
}

export default MyVinyls;