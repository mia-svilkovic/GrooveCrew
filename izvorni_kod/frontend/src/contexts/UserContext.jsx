import React, { createContext, useState, useContext, useEffect } from "react";
import { jwtDecode } from "jwt-decode";
import { refreshTokenRequest, getUserFromToken } from "../utils/authUtils";

const UserContext = createContext();

export const UserProvider = ({ children }) => {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const initializeAuth = async () => {
      const accessToken = localStorage.getItem("access");
      const refreshToken = localStorage.getItem("refresh");

      if (!accessToken && !refreshToken) {
        setUser(null);
        return;
      }

      try {
        if (accessToken) {
          const decoded = jwtDecode(accessToken);
          // Check if token is expired
          if (decoded.exp * 1000 > Date.now()) {
            const userData = await getUserFromToken(accessToken);
            setUser(userData);
            return;
          }
        }
        // If access token is expired or missing but we have refresh token
        if (refreshToken) {
          const newAccessToken = await refreshTokenRequest();
          console.log(newAccessToken) ;
          const userData = await getUserFromToken(newAccessToken);
          setUser(userData);
        }
        else{
          localStorage.removeItem("access");
          localStorage.removeItem("refresh");
          setUser(null);
        }
      } catch (error) {
        console.error("Auth initialization failed:", error);
        localStorage.removeItem("access");
          localStorage.removeItem("refresh");
          setUser(null);
      }
    };

    initializeAuth();
  }, []);

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

export const useUser = () => useContext(UserContext);