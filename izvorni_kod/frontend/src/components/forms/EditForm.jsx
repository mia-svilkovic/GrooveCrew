import React, { useState, useEffect } from "react";
import "./Form.css";
import "./editPhotos.css";

const URL = import.meta.env.VITE_API_URL;

function EditForm({ vinyl, onClose, onUpdate }) {
  const [formData, setFormData] = useState({
    catalog_number: vinyl.catalog_number,
    artist: vinyl.artist,
    album_name: vinyl.album_name,
    release_year: vinyl.release_year,
    genre_id: vinyl.genre.id,
    location: vinyl.location,
    available_for_exchange: vinyl.available_for_exchange,
    additional_description: vinyl.additional_description,
    record_condition_id: vinyl.record_condition.id,
    cover_condition_id: vinyl.cover_condition.id,
  });

  const [newPhotos, setNewPhotos] = useState([]);
  const [existingPhotos, setExistingPhotos] = useState(vinyl.photos || []);
  const [recordConditions, setRecordConditions] = useState([]);
  const [coverConditions, setCoverConditions] = useState([]);
  const [genres, setGenres] = useState([]);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [recordResponse, coverResponse, genresResponse] =
          await Promise.all([
            fetch(`${URL}/api/goldmine-conditions-record/`, {
              credentials: "include",
            }),
            fetch(`${URL}/api/goldmine-conditions-cover/`, {
              credentials: "include",
            }),
            fetch(`${URL}/api/genres/`, { credentials: "include" }),
          ]);

        const [recordData, coverData, genresData] = await Promise.all([
          recordResponse.json(),
          coverResponse.json(),
          genresResponse.json(),
        ]);

        setRecordConditions(recordData);
        setCoverConditions(coverData);
        setGenres(genresData);
      } catch (error) {
        console.error("Error fetching data:", error);
        setErrorMessage("Failed to load form data");
      }
    };

    fetchData();
  }, []);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleImagesChange = (event) => {
    setNewPhotos(Array.from(event.target.files));
  };

  const handleRemoveExistingPhoto = (photoId) => {
    setExistingPhotos((prev) => prev.filter((photo) => photo.id !== photoId));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const submitData = new FormData();
    Object.keys(formData).forEach((key) => {
      submitData.append(key, formData[key]);
    });

    newPhotos.forEach((photo, index) => {
      submitData.append(`new_photos[${index}]`, photo);
    });

    submitData.append(
      "existing_photo_ids",
      JSON.stringify(existingPhotos.map((photo) => photo.id))
    );

    try {
      const response = await fetch(`${URL}/api/records/edit/${vinyl.id}`, {
        method: "PUT",
        body: submitData,
        credentials: "include",
      });

      if (response.ok) {
        const updatedVinyl = await response.json();
        setSuccessMessage("Vinyl updated successfully!");
        setTimeout(() => {
          onUpdate(updatedVinyl);
        }, 2000);
      } else {
        const errorData = await response.json();
        setErrorMessage(errorData?.message || "Failed to update vinyl");
      }
    } catch (error) {
      console.error("Error updating vinyl:", error);
      setErrorMessage("Error updating vinyl. Please try again.");
    }
  };

  return (
    <div className="form-container">
      <h2>Edit Vinyl</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          name="catalog_number"
          value={formData.catalog_number}
          onChange={handleChange}
          placeholder="Catalog Number"
          required
        />

        <input
          type="text"
          name="artist"
          value={formData.artist}
          onChange={handleChange}
          placeholder="Artist"
          required
        />

        <input
          type="text"
          name="album_name"
          value={formData.album_name}
          onChange={handleChange}
          placeholder="Album Name"
          required
        />

        <input
          type="number"
          name="release_year"
          value={formData.release_year}
          onChange={handleChange}
          placeholder="Release Year"
          min="1900"
          required
        />

        <select
          name="genre_id"
          value={formData.genre_id}
          onChange={handleChange}
          required
        >
          <option value="">Select Genre</option>
          {genres.map((genre) => (
            <option key={genre.id} value={genre.id}>
              {genre.name}
            </option>
          ))}
        </select>

        <input
          type="text"
          name="location"
          value={formData.location}
          onChange={handleChange}
          placeholder="Location"
          required
        />

        <label>
          <input
            type="checkbox"
            name="available_for_exchange"
            checked={formData.available_for_exchange}
            onChange={handleChange}
          />
          Available for Exchange
        </label>

        <select
          name="record_condition_id"
          value={formData.record_condition_id}
          onChange={handleChange}
          required
        >
          <option value="">Record Condition</option>
          {recordConditions.map((condition) => (
            <option key={condition.id} value={condition.id}>
              {condition.name}
            </option>
          ))}
        </select>

        <select
          name="cover_condition_id"
          value={formData.cover_condition_id}
          onChange={handleChange}
          required
        >
          <option value="">Cover Condition</option>
          {coverConditions.map((condition) => (
            <option key={condition.id} value={condition.id}>
              {condition.name}
            </option>
          ))}
        </select>

        <textarea
          name="additional_description"
          value={formData.additional_description}
          onChange={handleChange}
          placeholder="Additional Description"
        />

        <div className="existing-photos">
          <h4>Current Photos:</h4>
          <div className="photo-grid">
            {existingPhotos.map((photo) => (
              <div key={photo.id} className="photo-item">
                <img src={photo.image} alt="Vinyl" className="thumbnail" />
                <button
                  type="button"
                  onClick={() => handleRemoveExistingPhoto(photo.id)}
                  className="remove-photo"
                >
                  Remove
                </button>
              </div>
            ))}
          </div>
        </div>

        <div className="new-photos">
          <h4>Add New Photos:</h4>
          <input
            type="file"
            accept="image/*"
            multiple
            onChange={handleImagesChange}
          />
          {newPhotos.length > 0 && (
            <p>{newPhotos.length} new photo(s) selected</p>
          )}
        </div>

        {errorMessage && <p className="error-message">{errorMessage}</p>}
        {successMessage && <p className="success-message">{successMessage}</p>}

        <button type="submit">Update Vinyl</button>
        <button type="button" onClick={onClose}>
          Cancel
        </button>
      </form>
    </div>
  );
}

export default EditForm;
