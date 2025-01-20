import React, { useState, useEffect } from "react";
import "./Form.css";

// Koristi environment varijablu za API URL
const URL = import.meta.env.VITE_API_URL;

function FormRegister({ onClose }) {
  const [firstName, setFirstName] = useState(""); // promijenjeno u first_name
  const [lastName, setLastName] = useState(""); // promijenjeno u last_name
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password1, setPassword1] = useState("");
  const [password2, setPassword2] = useState(""); // Dodano za potvrdu lozinke
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
    if (password1 !== password2) {
      setErrorMessage("Passwords do not match.");
      return;
    }

    try {
      const response = await fetch(`${URL}/api/users/register/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({
          first_name: firstName, // Mapirano na first_name
          last_name: lastName, // Mapirano na last_name
          username: username,
          email: email,
          password1: password1,
          password2: password2, // Poslano i polje za potvrdu lozinke
        }),
      });

      if (response.ok) {
        const data = await response.json();

        if (data.tokens) {
          localStorage.setItem("access", data.tokens.access);
          localStorage.setItem("refresh", data.tokens.refresh);
          console.log("Registration successful:", data);
          setSuccessMessage("Registration successful!");
        } else {
          console.log("No tokens received");
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
          value={password1}
          onChange={(e) => setPassword1(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Confirm Password"
          value={password2}
          onChange={(e) => setPassword2(e.target.value)}
          required
        />
        <button type="submit">Register</button>
      </form>
      {successMessage && <p className="success-message">{successMessage}</p>}
      {errorMessage && <p className="error-message">{errorMessage}</p>}
      <button className="close-button" onClick={onClose}>
        Close
      </button>
    </div>
  );
}

export default FormRegister;
