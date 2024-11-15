import React, { useState, useEffect } from "react";
import "./Form.css";

// Koristi environment varijablu za API URL
const URL = import.meta.env.VITE_API_URL;

function FormRegister({ onClose }) {
  const [firstName, setFirstName] = useState(""); // promijenjeno u first_name
  const [lastName, setLastName] = useState(""); // promijenjeno u last_name
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState(""); // Dodano za potvrdu lozinke
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => {
        setSuccessMessage("");
        onClose();
      }, 2000); // Message disappears after 2 seconds
      return () => clearTimeout(timer); // Clean up the timer when the component is unmounted or successMessage changes
    }
    if (errorMessage) {
      const timer = setTimeout(() => setErrorMessage(""), 5000);
      return () => clearTimeout(timer); // Clean up the timer when the component is unmounted or errorMessage changes
    }
  }, [successMessage, errorMessage]); // Run this effect when successMessage or errorMessage changes

  const handleRegister = async (event) => {
    event.preventDefault(); // Prevent default form submission
    if (password !== passwordConfirm) {
      setErrorMessage("Passwords do not match.");
      return;
    }

    try {
      const response = await fetch(`${URL}/api/auth/register/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          first_name: firstName, // Mapirano na first_name
          last_name: lastName, // Mapirano na last_name
          username: username,
          email: email,
          password: password,
          password_confirm: passwordConfirm, // Poslano i polje za potvrdu lozinke
        }),
      });

      if (response.ok) {
        const data = await response.json();

        if (data.access) {
          localStorage.setItem("jwt", data.access); // Pohrani token
          console.log("Registration successful:", data);
          setSuccessMessage("Registration successful!");
        } else {
          console.log("No token received");
          setErrorMessage("Registration failed. Please try again.");
        }
      } else {
        console.log("Registration failed");
        setErrorMessage("Something went wrong. Please try again later.");
      }
    } catch (error) {
      console.error("Error registering:", error);
      setErrorMessage(
        "Error registering. Please check your connection or try again."
      );
    }
  };

  return (
    <div className="form-container">
      <h2>REGISTER</h2>
      <form onSubmit={handleRegister}>
        <input
          type="text"
          placeholder="First Name"
          value={firstName}
          onChange={(e) => setFirstName(e.target.value)}
          required
        />
        <input
          type="text"
          placeholder="Last Name"
          value={lastName}
          onChange={(e) => setLastName(e.target.value)}
          required
        />
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Confirm Password"
          value={passwordConfirm}
          onChange={(e) => setPasswordConfirm(e.target.value)}
          required
        />
        <button type="submit" className="form-button">
          Register
        </button>
      </form>
      {successMessage && <p className="success-message">{successMessage}</p>}
      {errorMessage && <p className="error-message">{errorMessage}</p>}
      <button className="close-button form-button" onClick={onClose}>
        Close
      </button>
    </div>
  );
}

export default FormRegister;
