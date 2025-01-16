import React, { useState, useEffect } from "react";
import { useUser } from "../../contexts/UserContext";
import { useAuthRefresh } from '../../contexts/AuthRefresh';
import "./Form.css";

const URL = import.meta.env.VITE_API_URL;

export default function FormWishlistAdd({ onClose, onAddItem }) {
  const [catalogNumber, setCatalogNumber] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const { user } = useUser();
  const { authFetch } = useAuthRefresh();
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
      const token = localStorage.getItem("access");

      const response = await authFetch(`${URL}/api/wishlist/add/`, {
        method: "POST",
        body: JSON.stringify({
          record_catalog_number: catalogNumber, // Match the backend expectation
        }),
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error("Failed to add record to wishlist");
      }
      const newItem = await response.json(); // Parse the responsse

      onAddItem(newItem);
      setSuccessMessage("Record successfully added to wishlist!");
      setCatalogNumber(""); // Clear the input field
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
          value={catalogNumber}
          onChange={(e) => setCatalogNumber(e.target.value)}
          placeholder="Enter catalog number"
          className="release-mark-input"
          required
        />
        <button type="submit">Add to Wishlist</button>
        <button className="close-button" onClick={onClose}>
          Close
        </button>
      </form>
      {successMessage && (
        <div className="success-message">{successMessage}</div>
      )}
      {errorMessage && <div className="error-message">{errorMessage}</div>}
    </div>
  );
}
