import React, { useState, useEffect } from "react";
import { useUser } from "../../contexts/UserContext";
import "./Form.css"

const URL = import.meta.env.VITE_API_URL;

export default function FormWishlistAdd({ onClose, onAddItem }) {
  const [releaseMark, setReleaseMark] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const { user } = useUser();
  const userId = user.id;


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

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSuccessMessage("");
    setErrorMessage("");

    try {
      const response = await fetch(`${URL}wishlist/add/${releaseMark}/user/${userId}/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error("Failed to add release mark to wishlist");
      }
      onAddItem(releaseMark); 
      setSuccessMessage("Release mark successfully added to wishlist!");
      setReleaseMark(""); // Clear the input field
    } catch (error) {
      console.error("Error adding to wishlist:", error);
      setErrorMessage("Failed to add to wishlist. Please try again.");
    }
  };

  return (
    <div className="form-container">
      <form onSubmit={handleSubmit}>
        <h2>Add to Wishlist</h2>
          <input
            type="text"
            value={releaseMark}
            onChange={(e) => setReleaseMark(e.target.value)}
            placeholder="Enter release mark"
            className="release-mark-input"
            required
          />
        <button type="submit">Add to Wishlist</button>
        <button className="close-button" onClick={onClose}>
        Close
      </button>
      </form>
      {successMessage && <div className="success-message">{successMessage}</div>}
      {errorMessage && <div className="error-message">{errorMessage}</div>}
    </div>
  );
}
