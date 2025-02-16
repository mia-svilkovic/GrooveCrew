import React, { useState, useEffect } from "react";
import { useUser } from "../../contexts/UserContext"; // Importaj useUser hook
import "./Form.css";

// Koristi environment varijablu za API URL
const URL = import.meta.env.VITE_API_URL;


function FormLogin({ onClose, showMessage = false }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  // Koristi useUser hook za pristup i ažuriranje korisničkog stanja
  const { setUser } = useUser(); // Sada koristi setUser direktno

  const handleSuccessfulLogin = (userData, tokens) => {
    setSuccessMessage("Login successful!");
    
    setTimeout(() => {
      localStorage.setItem("access", tokens.access);
      localStorage.setItem("refresh", tokens.refresh);
      setUser(userData);
      onClose();
    }, 2000);
  };
  
  useEffect(() => {
    let errorTimer;
    if (errorMessage) {
      errorTimer = setTimeout(() => {
        setErrorMessage("");
      }, 5000);
    }
    return () => {
      if (errorTimer) clearTimeout(errorTimer);
    };
  }, [errorMessage]);

  const handleLogin = async (event) => {
    event.preventDefault();

    try {
      const response = await fetch(`${URL}/api/users/login/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: email,
          password: password,
        }),
        credentials: "include",
      });

      if (response.ok) {
        const data = await response.json();

        if (data.user.is_staff) {
          window.location.href = `${URL}/admin/`;
          return;
        }

        const userData = {
          id: data.user.id,
          email: data.user.email,
          username: data.user.username,
          first_name: data.user.first_name,
          last_name: data.user.last_name,
        };

        handleSuccessfulLogin(userData, data.tokens);

      } else {
        console.log("Login failed");
        setErrorMessage("Invalid credentials. Please try again.");
      }
    } catch (error) {
      console.error("Error logging in:", error);
      setErrorMessage("Error logging in. Please check your connection.");
    }
  };

  return (
    <div className="form-container">
      {showMessage && (
        <p className="note">Please log in to access this feature</p>
      )}
      <h2>LOG IN</h2>
      <form onSubmit={handleLogin}>
        <input
          type="email"
          placeholder="Email"
          name="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          name="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit">Login</button>
      </form>
      {successMessage && <p className="success-message">{successMessage}</p>}
      {errorMessage && <p className="error-message">{errorMessage}</p>}
      <button className="close-button" onClick={onClose}>
        Close
      </button>
    </div>
  );
}

export default FormLogin;
