import React, { useState } from "react";
import "./Form.css";

function FormLogin({ onClose }) {

  return (
    <div className="form-container">
      <h2>LOG IN</h2>
      <form>
        <input type="text" placeholder="Korisničko ime" required />
        <input type="password" placeholder="Lozinka" required />
        <button type="submit">Login</button>
      </form>
      <button className="close-button" onClick={onClose}>
        Close
      </button>
    </div>
  );
}

export default FormLogin;
