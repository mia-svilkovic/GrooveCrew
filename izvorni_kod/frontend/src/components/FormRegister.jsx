import React from "react";
import "./Form.css";

function FormRegister({ onClose }) {
  return (
    <div className="form-container">
      <h2>REGISTER</h2>
      <form>
        <input type="text" placeholder="Ime" required />
        <input type="text" placeholder="Prezime" required />
        <input type="text" placeholder="Korisničko ime" required />
        <input type="email" placeholder="Email" required />
        <input type="password" placeholder="Lozinka" required />
        <button type="submit">Register</button>
      </form>
      <button className="close-button" onClick={onClose}>
        Close
      </button>
    </div>
  );
}

export default FormRegister;
