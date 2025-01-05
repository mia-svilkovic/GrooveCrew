import React, { createContext, useState, useContext, useEffect } from "react";
import { jwtDecode } from "jwt-decode";

// Kreiramo kontekst
const UserContext = createContext();

// Provider komponenta koja omogućava pristup korisničkim podacima
export const UserProvider = ({ children }) => {
  const [user, setUser] = useState(null);

  // Restore user data from token on page load
  useEffect(() => {
    const initializeUser = () => {
      const accessToken = localStorage.getItem("access");

      if (accessToken) {
        try {
          const decoded = jwtDecode(accessToken);
          setUser({
            id: decoded.id,
            email: decoded.email,
            username: decoded.username,
            first_name: decoded.first_name,
            last_name: decoded.last_name,
          });
          console.log("User restored from token:", decoded);
        } catch (error) {
          console.error("Failed to decode token:", error);
          setUser(null);
        }
      }
    };

    initializeUser();
  }, []);

  // Logout function
  const logoutUser = () => {
    setUser(null);
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    console.log("User logged out and tokens cleared.");
  };

  return (
    <UserContext.Provider value={{ user, setUser, logoutUser }}>
      {children}
    </UserContext.Provider>
  );
};

// Custom Hook for User Context
export const useUser = () => useContext(UserContext);
