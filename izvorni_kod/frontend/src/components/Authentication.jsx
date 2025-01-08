import React, { useState } from "react";
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';
import "./Authentication.css";
import "./forms/Form.css" ;
import FormLogin from "./forms/FormLogin";
import FormRegister from "./forms/FormRegister";
import { useUser } from "../contexts/UserContext"; // Import useUser hook
import { useAuthRefresh } from '../contexts/AuthRefresh';

const URL = import.meta.env.VITE_API_URL;
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID


function Authentication() {
  const [activeForm, setActiveForm] = useState(null);
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);
  const { user, setUser, logoutUser } = useUser(); // Get user and logoutUser from context
  const { authFetch } = useAuthRefresh();

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

      const response = await authFetch(`${URL}/api/users/logout/`, {
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

  const handleGoogleLoginSuccess = async (credentialResponse) => {
    try {
      const idToken = credentialResponse.credential; // Google ID Token

      const response = await fetch(`${URL}/api/users/google-login/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ id_token: idToken }),
      });

      if (!response.ok) throw new Error('Google Login Failed');

      const data = await response.json();

      localStorage.setItem('access', data.tokens.access);
      localStorage.setItem('refresh', data.tokens.refresh);

      setUser({
        id: data.user.id,
        email: data.user.email,
        username: data.user.username,
        first_name: data.user.first_name,
        last_name: data.user.last_name,
      });

      console.log('Google Login Successful!');
    } catch (error) {
      console.error('Google Login Error:', error);
    }
  };

  const isLoggedIn = localStorage.getItem("access") !== null;

  console.log(user) ;
   return (
    <div className="auth-container">
      {isLoggedIn ? (
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
              <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
                <GoogleLogin
                  onSuccess={handleGoogleLoginSuccess}
                  onError={() => console.log('Google Login Failed')}
                />
              </GoogleOAuthProvider>
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
