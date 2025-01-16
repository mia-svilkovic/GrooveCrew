import { useUser } from './UserContext';
import { useNavigate } from 'react-router-dom';
import { refreshTokenRequest, getUserFromToken } from '../utils/authUtils';

export const useAuthRefresh = () => {
  const { logoutUser, setUser } = useUser();
  const navigate = useNavigate();

  const refreshToken = async () => {
    try {
      const newAccessToken = await refreshTokenRequest();
      setUser(getUserFromToken(newAccessToken));
      return newAccessToken;
    } catch (error) {
      console.log("error refreshing token");
      logoutUser();
      localStorage.clear('access');
      localStorage.clear('refresh');
      navigate('/');
    }
  };

  const authFetch = async (url, options = {}) => {
    try {
      let token = localStorage.getItem('access');
      
      const response = await fetch(url, {
        ...options,
        headers: {
          ...options.headers,
          Authorization: token && token.trim() ? `Bearer ${token}` : undefined,
        },
        credentials: 'include',
      });

      if (response.status === 401) {
        console.log("access token expired")
        token = await refreshToken();
        console.log(token);
        return fetch(url, {
          ...options,
          headers: {
            ...options.headers,
            Authorization: `Bearer ${token}`,
          },
          credentials: 'include',
        });
      }

      return response;
    } catch (error) {
      throw error ;
    }
  };

  return { authFetch };
};