import React, { useState } from "react";
import "./Authentication.css";
import FormLogin from "./forms/FormLogin";
import FormRegister from "./forms/FormRegister";

function Authentication() {
  const [activeForm, setActiveForm] = useState(null);

  const openLoginForm = () => setActiveForm("login");
  const openRegisterForm = () => setActiveForm("register");
  const closeForm = () => setActiveForm(null);

  return (
    <div className="auth-container">
      {!activeForm && (
        <>
          <button className="login-button" onClick={openLoginForm}>
            Login
          </button>
          <button className="register-button" onClick={openRegisterForm}>
            Register
          </button>
        </>
      )}
      {activeForm === "login" && (
        <div className="modal-overlay">
          <FormLogin onClose={closeForm} />
        </div>
      )}
      {activeForm === "register" && (
        <div className="modal-overlay">
          <FormRegister onClose={closeForm} />
        </div>
      )}
    </div>
  );
}

export default Authentication;
