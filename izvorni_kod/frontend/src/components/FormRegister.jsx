import React, { useState } from "react";
import "./Form.css";

function FormRegister({ onClose }) {
  const [name, setName] = useState("");
  const [lastname, setLastName] = useState("");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleRegister = async (event) => {
    event.preventDefault(); // Prevent default form submission
    console.log([name, lastname, username, email, password]);
    try {
      const response = await fetch("registerAuth/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          first_name: name,        // Map `name` to `first_name`
          last_name: lastname,     // Map `lastname` to `last_name`
          username: username,
          email: email,
          password: password,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        console.log("Registration successful:", data);
      } else {
        console.log("Registration failed");
      }
    } catch (error) {
      console.error("Error registering:", error);
    }
  };

  return (
    <div className="form-container">
      <h2>REGISTER</h2>
      <form onSubmit={handleRegister}>
        <input
          type="text"
          placeholder="Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />
        <input
          type="text"
          placeholder="Surname"
          value={lastname}
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
        <button type="submit">Register</button>
      </form>
      <button className="close-button" onClick={onClose}>
        Close
      </button>
    </div>
  );
}

export default FormRegister;
