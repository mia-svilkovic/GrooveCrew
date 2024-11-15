import React, { useState } from "react";
import "./Form.css";

// Koristi environment varijablu za API URL
const URL = import.meta.env.VITE_API_URL;

function FormAdd({ onClose }) {
  const [artist, setArtist] = useState("");
  const [albumName, setAlbumName] = useState("");
  const [releaseYear, setReleaseYear] = useState("");
  const [releaseCode, setReleaseCode] = useState("");
  const [genre, setGenre] = useState("");
  const [location, setLocation] = useState("");
  const [goldmineStandard, setGoldmineStandard] = useState("");
  const [additionalDescription, setAdditionalDescription] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const handleAddRecord = async (event) => {
    event.preventDefault();

    const formData = new FormData();
    formData.append("artist", artist);
    formData.append("album_name", albumName);
    formData.append("release_year", releaseYear);
    formData.append("release_code", releaseCode);
    formData.append("genre", genre);
    formData.append("location", location);
    formData.append("goldmine_standard", goldmineStandard);
    formData.append("additional_description", additionalDescription);

    try {
      const response = await fetch(`${URL}/add_record/`, {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        console.log("Record added successfully:", data);
        setSuccessMessage("Vinyl added successfully!");
        setErrorMessage(""); // Clear any previous error messages
        onClose(); // Call onClose after successful submission
      } else {
        const errorData = await response.json();
        console.error("Failed to add record:", errorData);
        setErrorMessage("Failed to add vinyl. Please try again.");
        setSuccessMessage(""); // Clear success message if there was an error
      }
    } catch (error) {
      console.error("Error adding record:", error);
      setErrorMessage("Error adding vinyl. Please check your connection.");
      setSuccessMessage(""); // Clear success message if there was an error
    }
  };

  return (
    <div className="form-container">
      <h2>ADD VINYL</h2>
      <form onSubmit={handleAddRecord}>
        <input
          type="text"
          placeholder="Artist"
          value={artist}
          onChange={(e) => setArtist(e.target.value)}
          required
        />
        <input
          type="text"
          placeholder="Record Name"
          value={albumName}
          onChange={(e) => setAlbumName(e.target.value)}
          required
        />
        <input
          type="number"
          placeholder="Publication Year"
          value={releaseYear}
          onChange={(e) => setReleaseYear(e.target.value)}
          required
          min="1900"
          max={new Date().getFullYear()} // Set to current year as max value
        />
        <input
          type="text"
          placeholder="Publication Identifier"
          value={releaseCode}
          onChange={(e) => setReleaseCode(e.target.value)}
          required
        />
        <input
          type="text"
          placeholder="Genre"
          value={genre}
          onChange={(e) => setGenre(e.target.value)}
          required
        />
        <select
          id="Goldmine selection"
          value={goldmineStandard}
          onChange={(e) => setGoldmineStandard(e.target.value)}
          required
        >
          <option value="" disabled>
            Goldmine Standard
          </option>
          <option value="M">M</option>
          <option value="NM">NM</option>
          <option value="E">E</option>
          <option value="VG">VG</option>
          <option value="G">G</option>
          <option value="P">P</option>
        </select>
        <input
          type="text"
          placeholder="Location"
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          required
        />
        <input
          type="text"
          placeholder="Caption"
          value={additionalDescription}
          onChange={(e) => setAdditionalDescription(e.target.value)}
        />
        <button type="submit">Add vinyl</button>
      </form>
      {successMessage && <p className="success-message">{successMessage}</p>}
      {errorMessage && <p className="error-message">{errorMessage}</p>}
      <button className="cancel-button" onClick={onClose}>
        Cancel
      </button>
    </div>
  );
}

export default FormAdd;
