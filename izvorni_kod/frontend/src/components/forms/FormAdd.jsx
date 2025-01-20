import React, { useState, useEffect } from "react";
import "./Form.css";
import { useUser } from "../../contexts/UserContext";
import { useAuthRefresh } from '../../contexts/AuthRefresh';
import PhotoUpload from '../addVinylComponents/PhotoUpload';
import BasicInfo from '../addVinylComponents/BasicInfo';
import GenreSelect from '../addVinylComponents/GenreSelect';
import LocationPicker from '../addVinylComponents/LocationPicker';
import ConditionSelect from '../addVinylComponents/ConditionSelect';
import Description from '../addVinylComponents/Description';


const URL = import.meta.env.VITE_API_URL;

function FormAdd({ onClose, onAddItem, recordConditions, coverConditions, genres }) {
  const { user } = useUser();
  const { authFetch } = useAuthRefresh();

  const [formState, setFormState] = useState({
    addPhotos: [],
    catalogNumber: "",
    artist: "",
    albumName: "",
    releaseYear: "",
    genre: "",
    location: { lat: 0, lng: 0 },
    additionalDescription: "",
    recordCondition: "",
    coverCondition: "",
  });
  const [photoPreviews, setPhotoPreviews] = useState([]);
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
    setFormState(prev => ({
      ...prev,
      addPhotos: [...prev.addPhotos, ...files]
    }));
    const previews = files.map(file => window.URL.createObjectURL(file));
    setPhotoPreviews(prev => [...prev, ...previews]);
    event.target.value = '';
  };

  const handleRemovePhoto = (index) => {
    setFormState(prev => ({
      ...prev,
      addPhotos: prev.addPhotos.filter((_, i) => i !== index)
    }));
    window.URL.revokeObjectURL(photoPreviews[index]);
    setPhotoPreviews(prev => prev.filter((_, i) => i !== index));
  };

  const handleAddRecord = async (event) => {
    event.preventDefault();
    const formData = new FormData();
    const locationData = {
        coordinates: {
          "latitude": formState.location.lat,
          "longitude": formState.location.lng
        }
    };
    console.log("Location data:", JSON.stringify(locationData));
    console.log("Form state location:", formState.location);
    
    
    formState.addPhotos.forEach((photo, index) => {
      formData.append(`add_photos[${index}]`, photo);
    });
    formData.append("catalog_number", formState.catalogNumber);
    formData.append("artist", formState.artist);
    formData.append("album_name", formState.albumName);
    formData.append("release_year", formState.releaseYear);
    formData.append("genre_id", formState.genre);
    formData.append("location_add", JSON.stringify(locationData));
    formData.append("additional_description", formState.additionalDescription);
    formData.append("record_condition_id", formState.recordCondition);
    formData.append("cover_condition_id", formState.coverCondition);

    console.log("Location being sent:", formData.get("location"));

    try {
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

  const handleFormChange = (field, value) => {
    setFormState(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <div className="form-container" id="add-form-container">
      <h2>ADD VINYL</h2>
      <form onSubmit={handleAddRecord} id="add-form">
        <BasicInfo 
          formData={formState} 
          onChange={handleFormChange}
        />
        
        <GenreSelect
          genres={genres}
          selectedGenre={formState.genre}
          onChange={(value) => handleFormChange('genre', value)}
        />
        
        <LocationPicker
          location={formState.location}
          onLocationChange={(value) => handleFormChange('location', value)}
        />
        
        <ConditionSelect
          conditions={recordConditions}
          type="Record"
          value={formState.recordCondition}
          onChange={(value) => handleFormChange('recordCondition', value)}
        />
        
        <ConditionSelect
          conditions={coverConditions}
          type="Cover"
          value={formState.coverCondition}
          onChange={(value) => handleFormChange('coverCondition', value)}
        />
        
        <Description
          value={formState.additionalDescription}
          onChange={(value) => handleFormChange('additionalDescription', value)}
        />
        
        <PhotoUpload
          photoPreviews={photoPreviews}
          onPhotoChange={handleImagesChange}
          onRemovePhoto={handleRemovePhoto}
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
