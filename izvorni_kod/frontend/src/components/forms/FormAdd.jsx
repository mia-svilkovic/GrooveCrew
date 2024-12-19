import React, { useState, useEffect } from "react";
import "./Form.css";
import { useUser } from "../../contexts/UserContext";


// Koristi environment varijablu za API URL
const URL = import.meta.env.VITE_API_URL;
//console.log(URL) ;

//const token = localStorage.getItem('access') ;

function FormAdd({ onClose, gStand }) {

  const { user } = useUser();
  const userId = user.id ;

  console.log(gStand);

  const [photo, setPhoto] = useState(null); // Holds the photo file directly
  const [artist, setArtist] = useState("");
  const [albumName, setAlbumName] = useState("");
  const [releaseYear, setReleaseYear] = useState("");
  const [releaseCode, setReleaseCode] = useState("");
  const [genre, setGenre] = useState("");
  const [location, setLocation] = useState("");
  //const [goldmineStandard, setGoldmineStandard] = useState("");
  const [additionalDescription, setAdditionalDescription] = useState("");
  const [releaseMark, setReleaseMark] = useState("");
  const [recordCondition, setRecordCondition] = useState("");
  const [sleeveCondition, setSleeveCondition] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => {
        setSuccessMessage("");
        onClose();
      }, 2000); // Poruka nestaje nakon 2 sekundi
      return () => clearTimeout(timer); // Čisti timer kad se komponenta demontira ili kada se promijeni successMessage
    }
    if (errorMessage) {
      const timer = setTimeout(() => setErrorMessage(""), 5000);
      return () => clearTimeout(timer); // Čisti timer kad se komponenta demontira ili kada se promijeni errorMessage
    }
  }, [successMessage, errorMessage]);


  const handleImageChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setPhoto(file); // Store the file directly
    }
  };

  const handleAddRecord = async (event) => {
    event.preventDefault();

    const formData = new FormData();
    formData.append("photo", photo)
    formData.append("artist", artist);
    formData.append("album_name", albumName);
    formData.append("release_year", releaseYear);
    formData.append("release_code", releaseCode);
    formData.append("genre", genre);
    formData.append("location", location);
    //formData.append("goldmine_standard", goldmineStandard);
    formData.append("additional_description", additionalDescription);
    formData.append("release_code", releaseMark) ;
    formData.append("record_condition", recordCondition) ;
    formData.append("cover_condition", sleeveCondition) ;

    const handleImageChange = (event) => {
      const file = event.target.files[0];
      if (file) {
        setPhoto(file); // Store the file directly
      }
    };

    try {
      const response = await fetch(`${URL}add/user/${userId}/`, {
        method: "POST",
        // headers: {
        //   //'Authorization': `Bearer ${localStorage.getItem('access') }`, 
        //   'Content-Type': 'application/json',
        // },
        body: formData,
        credentials: 'include', 
      });

      if (response.ok) {
        const data = await response.json();
        console.log("Record added successfully:", data);
        setSuccessMessage("Vinyl added successfully!");
        setErrorMessage(""); // Clear any previous error messages
        //onClose(); // Call onClose after successful submission
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
          id="Goldmine record"
          value={recordCondition}
          onChange={(e) => setRecordCondition(e.target.value)}
          required
        >
          <option value="" disabled>
            Record Goldmine Standard
          </option>
          {gStand.map(i => <option key={i.id} value={i.id}>{i.abbreviation}</option>)}
        </select> 
        <select
          id="Goldmine sleeve"
          value={sleeveCondition}
          onChange={(e) => setSleeveCondition(e.target.value)}
          required
        >
          <option value="" disabled>
            Sleeve Goldmine Standard
          </option>
          {gStand.map(i => <option key={i.id} value={i.id}>{i.abbreviation}</option>)}
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
        <input
          type="text"
          placeholder="release mark"
          value={releaseMark}
          onChange={(e) => setReleaseMark(e.target.value)}
          required
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
