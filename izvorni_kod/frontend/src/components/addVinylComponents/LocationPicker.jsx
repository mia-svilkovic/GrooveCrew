import React from 'react';
import { MapContainer, TileLayer, Marker, useMapEvents } from "react-leaflet";
import "leaflet/dist/leaflet.css";

const LocationSelector = ({ onLocationChange }) => {
  useMapEvents({
    click: (e) => {
      onLocationChange({ lat: e.latlng.lat, lng: e.latlng.lng });
    },
  });

  return null;
};

const LocationPicker = ({ location, onLocationChange }) => {
  return (
    <div>
      <label>Location</label>
      <MapContainer center={[location.lat, location.lng]} zoom={2} style={{ height: "300px", width: "100%" }}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        <LocationSelector onLocationChange={onLocationChange} />
        {location && <Marker position={[location.lat, location.lng]} />}
      </MapContainer>
      <p>Selected Location: {location.lat}, {location.lng}</p>
    </div>
  );
};

export default LocationPicker;