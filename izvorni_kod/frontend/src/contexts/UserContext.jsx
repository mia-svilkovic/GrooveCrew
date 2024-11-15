import React, { createContext, useState, useContext } from "react";

// Kreiramo kontekst
const UserContext = createContext();

// Provider komponenta koja omogućava pristup korisničkim podacima
export const UserProvider = ({ children }) => {
  const [user, setUser] = useState(null); // Ovdje setUser ostaje kao funkcija za ažuriranje stanja

  const logoutUser = () => {
    setUser(null); // Briše korisničke podatke
  };

  return (
    <UserContext.Provider value={{ user, setUser, logoutUser }}>
      {" "}
      {/* SetUser ostaje kao funkcija */}
      {children}
    </UserContext.Provider>
  );
};

// Hook za dohvat korisničkih podataka i funkcija za login/logout
export const useUser = () => useContext(UserContext);
