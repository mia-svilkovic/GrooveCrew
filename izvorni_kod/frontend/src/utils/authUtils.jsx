import { jwtDecode } from "jwt-decode";

const URL = import.meta.env.VITE_API_URL;

export const refreshTokenRequest = async () => {
  const refresh = localStorage.getItem('refresh');
  
  if (!refresh) {
    throw new Error('No refresh token available');
  }

  const response = await fetch(`${URL}/api/token/refresh/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ refresh }),
  });

  if (!response.ok) {
    throw new Error('Token refresh failed');
  }

  const data = await response.json();
  localStorage.setItem('access', data.access);
  return data.access;
};

export const getUserFromToken = (token) => {
    const decoded = jwtDecode(token);
      return {
        id: decoded.user_id,
        email: decoded.email,
        username: decoded.username,
        first_name: decoded.first_name,
        last_name: decoded.last_name,
      };
};
