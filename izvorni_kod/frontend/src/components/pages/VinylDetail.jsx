import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useUser } from "../../contexts/UserContext";
import exchange from "../../assets/images/exchange.png";
import ExchangeForm from "../forms/ExchangeForm";
import "./VinylDetail.css";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";

const URL = import.meta.env.VITE_API_URL;

function VinylDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useUser();
  const [vinyl, setVinyl] = useState(null);
  const [selectedPhoto, setSelectedPhoto] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [coordinates, setCoordinates] = useState(null);
  const [showExchangeForm, setShowExchangeForm] = useState(false);

  useEffect(() => {
    if(!user) {
      navigate('/');
      return;
    }
    const fetchVinylDetails = async () => {
      try {
        const response = await fetch(`${URL}/api/records/${id}/`, {
          method: "GET",
        });

        if (!response.ok) {
          throw new Error("Failed to fetch vinyl details");
        }

        const data = await response.json();
        setVinyl(data);
        console.log(vinyl);
        
        if (data.photos && data.photos.length > 0) {
          setSelectedPhoto(data.photos[0].image);
        }

        if (data.location?.coordinates) {
          const match = data.location.coordinates.match(/POINT \(([^)]+)\)/);
          if (match) {
            const [longitude, latitude] = match[1].split(" ").map(Number);
            setCoordinates({ latitude, longitude });
          }
        }
        
        setLoading(false);
      } catch (error) {
        console.error("Error fetching vinyl details:", error);
        setError("Failed to load vinyl details. Please try again.");
        setLoading(false);
      }
    };

    fetchVinylDetails();
  }, [id]);

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  if (!vinyl) {
    return <div className="not-found">Vinyl not found</div>;
  }

  const handleUserClick = (userId) => {
    navigate(`/user/${userId}`);
  };

  const handleExchangeClick = (e) => {
    e.preventDefault();
    setShowExchangeForm(true);
  };

  return (
    <div className="vinyl-detail-container">
      <button onClick={() => navigate(-1)} className="back-button">
        ← Back
      </button>

      <div className="vinyl-detail-content">
        <div className="vinyl-header">
          <h1>{vinyl.album_name}</h1>
          <h2>by {vinyl.artist}</h2>
        </div>
      </div>

      <div className="vinyl-main-content">
        <div className="photos-section">
          <div className="main-photo">
            {selectedPhoto && <img src={selectedPhoto} alt={vinyl.album_name} />}
          </div>
          {vinyl.photos?.length > 1 && (
            <div className="photo-thumbnails">
              {vinyl.photos.map((photo) => (
                <img
                  key={photo.id}
                  src={photo.image}
                  alt={`${vinyl.album_name} thumbnail`}
                  onClick={() => setSelectedPhoto(photo.image)}
                  className={selectedPhoto === photo.image ? "selected" : ""}
                />
              ))}
            </div>
          )}
        </div>

        <div className="details-section">
          <div className="info-card">
            <h3>Album Details</h3>
            <div className="info-grid">
              <div className="info-item">
                <span className="label">Release Year:</span>
                <span className="value">{vinyl.release_year}</span>
              </div>
              <div className="info-item">
                <span className="label">Genre:</span>
                <span className="value">{vinyl.genre?.name}</span>
              </div>
              <div className="info-item">
                <span className="label">Catalog Number:</span>
                <span className="value">{vinyl.catalog_number}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="info-card">
          <h3>Location</h3>
          <div>
            {vinyl.location?.city}, {vinyl.location?.country}    
          </div>
          {coordinates ? (
            <MapContainer
              center={[coordinates.latitude, coordinates.longitude]}
              zoom={13}
              style={{ height: "300px", width: "100%" }}
            >
              <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              />
              <Marker position={[coordinates.latitude, coordinates.longitude]}>
                <Popup>
                  {vinyl.location?.address} <br />
                  {vinyl.location?.city}, {vinyl.location?.country}
                </Popup>
              </Marker>
            </MapContainer>  
          ) : (
            <p>No location information available.</p>
          )}
        </div>

        <div className="info-card">
          <h3>Condition</h3>
          <div className="condition-details">
            <div className="condition-item">
              <h4>
                Record Condition: {vinyl.record_condition?.name} (
                {vinyl.record_condition?.abbreviation})
              </h4>
              <p>{vinyl.record_condition?.description}</p>
            </div>
            <div className="condition-item">
              <h4>
                Cover Condition: {vinyl.cover_condition?.name} (
                {vinyl.cover_condition?.abbreviation})
              </h4>
              <p>{vinyl.cover_condition?.description}</p>
            </div>
          </div>
        </div>

        <div className="info-card">
          <h3>Additional Information</h3>
          <p className="description">{vinyl.additional_description}</p>
        </div>

        <div className="info-card">
          <h3>Owner Information</h3>
          <div className="owner-info">
            <p>
              {vinyl.user?.first_name} {vinyl.user?.last_name}
            </p>
            <p>Username: {vinyl.user?.username}</p>
            <p>Contact: {vinyl.user?.email}</p>
          </div>
          <button
            onClick={() => handleUserClick(vinyl.user?.id)}
            className="vinyl-opt"
          >
            <p>See owner profile</p>
          </button>
        </div>

        {vinyl.available_for_exchange && (
          <div className="exchange-section">
            <div className="exchange-badge">Available for Exchange</div>
            {user && user.username !== vinyl.user?.username && (
              <button className="vinyl-opt" onClick={handleExchangeClick}>
                <p>Offer exchange</p>
                <img src={exchange} alt="Request Exchange" />
              </button>
            )}
          </div>
        )}
      </div>

      {showExchangeForm && (
        <div className="modal-overlay">
          <ExchangeForm
            selectedVinylId={id}
            onClose={() => setShowExchangeForm(false)}
          />
        </div>
      )}
    </div>
  );
}

export default VinylDetail;