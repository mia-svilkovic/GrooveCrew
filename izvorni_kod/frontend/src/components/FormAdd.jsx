import React, { useState } from "react";
import "./Form.css";

function FormAdd({ onClose }) {
  const [photo, setPhoto] = useState(null); // Holds binary data of the photo
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
      const reader = new FileReader();
      reader.onloadend = () => {
        setPhoto(Array.from(new Uint8Array(reader.result))); // Convert to binary array
      };
      reader.readAsArrayBuffer(file); // Read file as binary
    }
  };

  const handleAddRecord = async (event) => {
    event.preventDefault();

    try {
      const response = await fetch("add_record/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          photo: photo, // Binary array data
          artist: artist,
          album_name: albumName,
          release_year: releaseYear,
          release_code: releaseCode,
          genre: genre,
          location: location,
          goldmine_standard: goldmineStandard,
          additional_description: additionalDescription,
        }),
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
      <button className="cancle-button" onClick={onClose}>
        Cancel
      </button>
    </div>
  );
}

export default FormAdd;
