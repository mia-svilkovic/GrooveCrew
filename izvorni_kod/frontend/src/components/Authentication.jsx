import React, { useState } from "react";
import "./Authentication.css";
import "./forms/Form.css" ;
import FormLogin from "./forms/FormLogin";
import FormRegister from "./forms/FormRegister";
import { useUser } from "../contexts/UserContext"; // Import useUser hook

const URL = import.meta.env.VITE_API_URL;


function Authentication() {
  const [activeForm, setActiveForm] = useState(null);
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);
  const { user, logoutUser } = useUser(); // Get user and logoutUser from context

  const openLoginForm = () => setActiveForm("login");
  const openRegisterForm = () => setActiveForm("register");
  const closeForm = () => setActiveForm(null);

  const handleLogoutClick = () => {
    setShowLogoutConfirm(true);
  };

  const handleLogout = async () => {
    try {
      const refreshToken = localStorage.getItem('refresh');
      const accessToken = localStorage.getItem('access');

      const response = await fetch(`${URL}/api/users/logout/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh: refreshToken })
      });
      if (!response.ok) {
        throw new Error('Logout failed');
      }
      logoutUser();
      closeForm();
      setShowLogoutConfirm(false);
      
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const isLoggedIn = localStorage.getItem("access") !== null;

  console.log(user) ;
   return (
    <div className="auth-container">
      {user?.username ? (
        <>
        <button className="logout-button" onClick={handleLogoutClick}>
          Logout
        </button>
        {showLogoutConfirm && (
          <div className="modal-overlay">
            <div className="form-container">
              <h2>Are you sure?</h2>
              <p>Log out from {user.username}?</p>
              
              <button 
                className="close-button"
                onClick={() => setShowLogoutConfirm(false)}
              >
                Cancel
              </button>
              <button 
                className="confirm-button" 
                onClick={handleLogout}
              >
                Logout
              </button>
        
            </div>
          </div>
        )}
      </>
      ) : (
        <>
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
        </>
      )}
    </div>
  );
}

export default Authentication;
