import React, { useState } from "react";
import './Form.css'

function FormAdd({ onClose }) {

    const [selectedOption, setSelectedOption] = useState('')
    const [selectedImage, setSelectedImage] = useState('')
    const handleChange = (event) =>{
      setSelectedOption(event.target.value)
    }
    const handleImageChange = (event) => {
      const file = event.target.files[0];
      if (file){
        selectedImage(file);
      }
    }

    return (
      <div className="form-container">
        <h2>ADD VINYL</h2>
        <form>
          <lable htmlFor="chooseImage">Cover image:</lable>
          <input type="file" id="chooseImage" accept="image/*" onChange={handleImageChange} required></input>
          <input type="text" placeholder="Artist" required />
          <input type="text" placeholder="Record Name" required />
          <input type="number" placeholder="Publication Year" required />
          <input type="text" placeholder="Publication Identificator" required />
          <input type="text" placeholder="Genre" required />
          <select
            id="Goldmine selection"
            value={selectedOption}
            onChange={handleChange}
            required
          >
            <option value="" disabled>Goldmind standard</option>
            <option value="M">M</option>
            <option value="NM">NM</option>
            <option value="E">E</option>
            <option value="VG">VG</option>
            <option value="G">G</option>
            <option value="P">P</option>
          </select>

          <input type="text" placeholder="Location" required />
          <input type="text" placeholder="Caption"/>
          <button type="submit">Add vinyl</button>
        </form>
        <button className="cancle-button" onClick={onClose}>
          Cancle
        </button>
      </div>
    );
  }
  
  export default FormAdd;