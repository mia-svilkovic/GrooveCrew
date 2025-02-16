import React, { useState } from 'react';
import "./Form.css"
import { useAuthRefresh } from '../../contexts/AuthRefresh';

const URL = import.meta.env.VITE_API_URL;

function DeleteForm({ vinyl, onClose, onDelete }) {
  const [errorMessage, setErrorMessage] = useState("");
  const { authFetch } = useAuthRefresh();
  

  const handleDelete = async () => {
    try {
      const token = localStorage.getItem("access");
      const response = await authFetch(`${URL}/api/records/${vinyl.id}/delete/`, {
        method: 'DELETE',
      });

      if (response.ok) {
        onDelete(vinyl.id);
      } else {
        const errorData = await response.json();
        setErrorMessage(errorData?.message || 'Failed to delete vinyl');
      }
    } catch (error) {
      console.error('Error deleting vinyl:', error);
      setErrorMessage('Error deleting vinyl. Please try again.');
    }
  };

  return (
    <div className="form-container">
      <h2>Delete Vinyl</h2>
      <p>Are you sure you want to delete "{vinyl.album_name}" by {vinyl.artist}?</p>
      <p className="note">Note: this action can not be undone</p>
      
      {errorMessage && <p className="error-message">{errorMessage}</p>}
      
      
        <button onClick={handleDelete} className="delete-button">Delete</button>
        <button onClick={onClose} className="cancel-button">Cancel</button>
      
    </div>
  );
}

export default DeleteForm;