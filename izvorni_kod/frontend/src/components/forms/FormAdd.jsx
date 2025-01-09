import React, { useState, useEffect } from "react";
import "./Form.css";
import { useUser } from "../../contexts/UserContext";
import { useAuthRefresh } from '../../contexts/AuthRefresh';

const URL = import.meta.env.VITE_API_URL;

function FormAdd({
  onClose,
  onAddItem,
  recordConditions,
  coverConditions,
  genres,
}) {
  const { user } = useUser();
  const { authFetch } = useAuthRefresh();

  const [addPhotos, setAddPhotos] = useState([]);
  const [catalogNumber, setCatalogNumber] = useState("");
  const [artist, setArtist] = useState("");
  const [albumName, setAlbumName] = useState("");
  const [releaseYear, setReleaseYear] = useState("");
  const [genre, setGenre] = useState("");
  const [location, setLocation] = useState("");
  const [additionalDescription, setAdditionalDescription] = useState("");
  const [recordCondition, setRecordCondition] = useState("");
  const [coverCondition, setCoverCondition] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [photoPreviews, setPhotoPreviews] = useState([]);


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
    setAddPhotos(prev => [...prev, ...files]);
    const previews = files.map(file => window.URL.createObjectURL(file));
    setPhotoPreviews(prev => [...prev, ...previews]);
    event.target.value = '';
  };

  const handleAddRecord = async (event) => {
    event.preventDefault();
    console.log(addPhotos) ;

    const formData = new FormData();
    addPhotos.forEach((photo, index) => {
      formData.append(`add_photos[${index}]`, photo);
    });
    formData.append("catalog_number", catalogNumber);
    formData.append("artist", artist);
    formData.append("album_name", albumName);
    formData.append("release_year", releaseYear);
    formData.append("genre_id", genre);
    formData.append("location", location);
    formData.append("additional_description", additionalDescription);
    formData.append("record_condition_id", recordCondition);
    formData.append("cover_condition_id", coverCondition);

    try {
      const token = localStorage.getItem("access");

      const response = await authFetch(`${URL}/api/records/create/`, {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        setSuccessMessage("Vinyl added successfully!");
        const newItem = await response.json();
        onAddItem(newItem);
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

  useEffect(() => {
    return () => {
      photoPreviews.forEach(preview => window.URL.revokeObjectURL(preview));
    };
  }, [photoPreviews]);

  const handleRemovePhoto = (index) => {
    setAddPhotos(prev => prev.filter((_, i) => i !== index));
    window.URL.revokeObjectURL(photoPreviews[index]);
    setPhotoPreviews(prev => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="form-container" >
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
          min="1900"
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

        {photoPreviews.length > 0 && (
          <div className="existing-photos">
            <h4>Selected Photos:</h4>
            <div className="photo-grid">
              {photoPreviews.map((preview, index) => (
                <div key={index} className="photo-item">
                  <img src={preview} alt="Preview" className="thumbnail" />
                  <button
                    type="button"
                    onClick={() => handleRemovePhoto(index)}
                    className="remove-photo"
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        <input
          type="file"
          accept="image/*"
          multiple
          style={{ color: 'transparent' }}
          onChange={handleImagesChange}
        />
        {/* {addPhotos.length > 0 && (
            <span className="note">
              {addPhotos.length} file{addPhotos.length !== 1 ? 's' : ''} selected
            </span>
        )} */}

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
