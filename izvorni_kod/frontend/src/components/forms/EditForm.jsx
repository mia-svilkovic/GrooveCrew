import React, { useState, useEffect } from "react";
import "./Form.css";
import "./editPhotos.css";
import { useAuthRefresh } from '../../contexts/AuthRefresh';
import PhotoUpload from '../addVinylComponents/PhotoUpload';
import BasicInfo from '../addVinylComponents/BasicInfo';
import GenreSelect from '../addVinylComponents/GenreSelect';
import LocationPicker from '../addVinylComponents/LocationPicker';
import ConditionSelect from '../addVinylComponents/ConditionSelect';
import Description from '../addVinylComponents/Description';

const URL = import.meta.env.VITE_API_URL;

function EditForm({ vinyl, onClose, onUpdate }) {
  const [formData, setFormData] = useState({
    catalog_number: vinyl.catalog_number,
    artist: vinyl.artist,
    album_name: vinyl.album_name,
    release_year: vinyl.release_year,
    genre_id: vinyl.genre.id,
    location: JSON.stringify(vinyl.location),
    additional_description: vinyl.additional_description,
    record_condition_id: vinyl.record_condition.id,
    cover_condition_id: vinyl.cover_condition.id,
  });

  const [addPhotos, setAddPhotos] = useState([]);
  const [photoPreviews, setPhotoPreviews] = useState([]);
  const [recordConditions, setRecordConditions] = useState([]);
  const [coverConditions, setCoverConditions] = useState([]);
  const [genres, setGenres] = useState([]);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const { authFetch } = useAuthRefresh();

  useEffect(() => {
    const fetchExistingPhotos = async () => {
      try {
        const existingPhotosPromises = vinyl.photos.map(async (photo) => {
          const response = await fetch(photo.image);
          const blob = await response.blob();
          const file = new File([blob], `photo-${photo.id}.jpg`, { type: 'image/jpeg' });
          return file;
        });

        const existingPhotoFiles = await Promise.all(existingPhotosPromises);
        setAddPhotos(existingPhotoFiles);
        setPhotoPreviews(vinyl.photos.map(photo => photo.image));
      } catch (error) {
        console.error("Error fetching existing photos:", error);
        setErrorMessage("Failed to load existing photos");
      }
    };

    fetchExistingPhotos();
  }, [vinyl.photos]);

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
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleImagesChange = (event) => {
    const files = Array.from(event.target.files);
    setAddPhotos(prev => [...prev, ...files]);
    const previews = files.map(file => window.URL.createObjectURL(file));
    setPhotoPreviews(prev => [...prev, ...previews]);
    event.target.value = '';
  };

  const handleRemovePhoto = (index) => {
    setAddPhotos(prev => prev.filter((_, i) => i !== index));
    window.URL.revokeObjectURL(photoPreviews[index]);
    setPhotoPreviews(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const submitData = new FormData();
    Object.keys(formData).forEach((key) => {
      submitData.append(key, formData[key]);
    });

    addPhotos.forEach((photo, index) => {
      submitData.append(`add_photos[${index}]`, photo);
    });

    try {
      const response = await authFetch(`${URL}/api/records/${vinyl.id}/update/`, {
        method: "PUT",
        body: submitData,
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

  useEffect(() => {
    return () => {
      photoPreviews.forEach(preview => {
        if (preview.startsWith('blob:')) {
          window.URL.revokeObjectURL(preview);
        }
      });
    };
  }, [photoPreviews]);

  return (
    <div className="form-container">
      <h2>Edit Vinyl</h2>
      <form onSubmit={handleSubmit}>
        <BasicInfo formData={formData} onChange={handleChange} />
        
        <GenreSelect
          genres={genres}
          selectedGenre={formData.genre_id}
          onChange={handleChange}
        />
        
        <LocationPicker
          location={formData.location}
          onLocationChange={handleChange}
        />
        
        <ConditionSelect
          conditions={recordConditions}
          type="Record"
          value={formData.record_condition_id}
          onChange={handleChange}
        />
        
        <ConditionSelect
          conditions={coverConditions}
          type="Cover"
          value={formData.cover_condition_id}
          onChange={handleChange}
        />
        
        <Description
          value={formData.additional_description}
          onChange={handleChange}
        />
        
        <PhotoUpload
          photoPreviews={photoPreviews}
          onPhotoChange={handleImagesChange}
          onRemovePhoto={handleRemovePhoto}
        />

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