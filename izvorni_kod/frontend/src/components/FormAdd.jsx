import React, { useState } from "react";
import "./Form.css";
URL = "http://localhost:8000";

function FormAdd({ onClose }) {
  const [photo, setPhoto] = useState(null); // Holds the photo file directly
  const [artist, setArtist] = useState("");
  const [albumName, setAlbumName] = useState("");
  const [releaseYear, setReleaseYear] = useState("");
  const [releaseCode, setReleaseCode] = useState("");
  const [genre, setGenre] = useState("");
  const [location, setLocation] = useState("");
  const [goldmineStandard, setGoldmineStandard] = useState("");
  const [additionalDescription, setAdditionalDescription] = useState("");

  const handleImageChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setPhoto(file); // Store the file directly
    }
  };

  const handleAddRecord = async (event) => {
    event.preventDefault();

    const formData = new FormData();
    formData.append("photo", photo); // Add the file directly
    formData.append("artist", artist);
    formData.append("album_name", albumName);
    formData.append("release_year", releaseYear);
    formData.append("release_code", releaseCode);
    formData.append("genre", genre);
    formData.append("location", location);
    formData.append("goldmine_standard", goldmineStandard);
    formData.append("additional_description", additionalDescription);

    try {
      const response = await fetch("add_record/", {
        method: "POST",
        body: formData, // Send the form data directly
      });

      if (response.ok) {
        const data = await response.json();
        console.log("Record added successfully:", data);
      } else {
        console.error("Failed to add record");
      }
    } catch (error) {
      console.error("Error adding record:", error);
    }
  };

  return (
    <div className="form-container">
      <h2>ADD VINYL</h2>
      <form onSubmit={handleAddRecord}>
        <label htmlFor="chooseImage">Cover image:</label>
        <input
          type="file"
          id="chooseImage"
          accept="image/*"
          onChange={handleImageChange}
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
      <button className="cancel-button" onClick={onClose}>
        Cancel
      </button>
    </div>
  );
}

export default FormAdd;
