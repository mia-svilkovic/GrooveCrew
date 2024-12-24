import React, { useState, useEffect } from "react";
import "./Form.css";
import { useUser } from "../../contexts/UserContext";

const URL = import.meta.env.VITE_API_URL;

function FormAdd({ onClose, recordConditions, coverConditions, genres }) {
  const { user } = useUser();

  const [photos, setPhotos] = useState([]);
  const [catalogNumber, setCatalogNumber] = useState("");
  const [artist, setArtist] = useState("");
  const [albumName, setAlbumName] = useState("");
  const [releaseYear, setReleaseYear] = useState("");
  const [genre, setGenre] = useState("");
  const [location, setLocation] = useState("");
  const [additionalDescription, setAdditionalDescription] = useState("");
  const [recordCondition, setRecordCondition] = useState("");
  const [coverCondition, setCoverCondition] = useState("");
  const [availableForExchange, setAvailableForExchange] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

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

  const handleImagesChange = (event) => {
    const files = Array.from(event.target.files);
    setPhotos(files);
  };

  const handleAddRecord = async (event) => {
    event.preventDefault();

    const formData = new FormData();
    photos.forEach((photo, index) => {
      formData.append(`photos[${index}]`, photo);
    });
    formData.append("catalog_number", catalogNumber);
    formData.append("artist", artist);
    formData.append("album_name", albumName);
    formData.append("release_year", releaseYear);
    formData.append("genre_id", genre);
    formData.append("location", location);
    formData.append("available_for_exchange", availableForExchange);
    formData.append("additional_description", additionalDescription);
    formData.append("record_condition_id", recordCondition);
    formData.append("cover_condition_id", coverCondition);

    try {
      const token = localStorage.getItem("access");

      const response = await fetch(`${URL}/api/records/add/`, {
        method: "POST",
        body: formData,
        credentials: "include",
        headers: {
          Authorization: token ? `Bearer ${token}` : "",
        },
      });

      if (response.ok) {
        setSuccessMessage("Vinyl added successfully!");
      } else {
        const errorData = await response.json();
        setErrorMessage(
          errorData?.error ||
            errorData?.message ||
            "Failed to add vinyl. Please try again."
        );
      }
    } catch (error) {
      console.error("Error adding record:", error);
      setErrorMessage("Error adding vinyl. Please check your connection.");
    }
  };

  return (
    <div className="form-container">
      <h2>ADD VINYL</h2>
      <form onSubmit={handleAddRecord}>
        <input
          type="text"
          placeholder="Catalog Number"
          value={catalogNumber}
          onChange={(e) => setCatalogNumber(e.target.value)}
          required
        />

        <input
          type="text"
          placeholder="Artist"
          value={artist}
          onChange={(e) => setArtist(e.target.value)}
          required
        />

        <input
          type="text"
          placeholder="Album Name"
          value={albumName}
          onChange={(e) => setAlbumName(e.target.value)}
          required
        />

        <input
          type="number"
          placeholder="Release Year"
          value={releaseYear}
          onChange={(e) => setReleaseYear(e.target.value)}
          required
        />

        <select
          value={genre}
          onChange={(e) => setGenre(e.target.value)}
          required
        >
          <option value="">Select Genre</option>
          {genres.map((item) => (
            <option key={item.id} value={item.id}>
              {item.name}
            </option>
          ))}
        </select>

        <label>Location</label>
        <input
          type="text"
          placeholder="Location"
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          required
        />

        <label>
          <input
            type="checkbox"
            checked={availableForExchange}
            onChange={(e) => setAvailableForExchange(e.target.checked)}
          />
          Available for Exchange
        </label>

        <select
          value={recordCondition}
          onChange={(e) => setRecordCondition(e.target.value)}
          required
        >
          <option value="">Record Condition</option>
          {recordConditions.map((item) => (
            <option key={item.id} value={item.id}>
              {item.name}
            </option>
          ))}
        </select>

        <select
          value={coverCondition}
          onChange={(e) => setCoverCondition(e.target.value)}
          required
        >
          <option value="">Cover Condition</option>
          {coverConditions.map((item) => (
            <option key={item.id} value={item.id}>
              {item.name}
            </option>
          ))}
        </select>

        <textarea
          placeholder="Additional Description"
          value={additionalDescription}
          onChange={(e) => setAdditionalDescription(e.target.value)}
        ></textarea>

        <input
          type="file"
          accept="image/*"
          multiple
          onChange={handleImagesChange}
        />

        <button type="submit">Add Vinyl</button>
        <button className="close-button" onClick={onClose}>
          Close
        </button>
      </form>
      {successMessage && <p className="success-message">{successMessage}</p>}
      {errorMessage && <p className="error-message">{errorMessage}</p>}
    </div>
  );
}

export default FormAdd;
