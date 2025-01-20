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

  let coordinates = { lat: 0, lng: 0 } ;
  if (vinyl.location?.coordinates) {
    const match = vinyl.location.coordinates.match(/POINT \(([^)]+)\)/);
    if (match) {
      const [longitude, latitude] = match[1].split(" ").map(Number);
      coordinates = { lat:latitude, lng:longitude };
    }
  }

  console.log(coordinates) ;
  
  const [formState, setFormState] = useState({
    catalogNumber: vinyl.catalog_number,
    artist: vinyl.artist,
    albumName: vinyl.album_name,
    releaseYear: vinyl.release_year,
    genre: vinyl.genre.id,
    location: coordinates,
    additionalDescription: vinyl.additional_description,
    recordCondition: vinyl.record_condition.id,
    coverCondition: vinyl.cover_condition.id,
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
    const formData = new FormData();
    const locationData = {
        coordinates: {
          "latitude": formState.location.lat,
          "longitude": formState.location.lng
        }
    };
    console.log("Location data:", JSON.stringify(locationData));
    console.log("Form state location:", formState.location);
    
    
    addPhotos.forEach((photo, index) => {
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

    console.log("Location being sent:", formData.get("location_add"));
    try {
      const response = await authFetch(`${URL}/api/records/${vinyl.id}/update/`, {
        method: "PUT",
        body: formData,
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

  const handleFormChange = (field, value) => {
    setFormState(prev => ({
      ...prev,
      [field]: value
    }));
    console.log(formState) ;
  };

  return (
    <div className="form-container">
      <h2>UPDATE VINYL</h2>
      <form onSubmit={handleSubmit}>
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

        <button type="submit">Update Vinyl</button>
        <button className="close-button" onClick={onClose}>
          Close
        </button>
      </form>
      
      {successMessage && <p className="success-message">{successMessage}</p>}
      {errorMessage && <p className="error-message">{errorMessage}</p>}
    </div>
  );
}

export default EditForm;