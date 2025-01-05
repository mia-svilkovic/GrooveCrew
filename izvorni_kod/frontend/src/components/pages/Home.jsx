import AddVinyl from "../AddVinyl";
import AllVinyls from "../AllVinyls";
import { useUser } from "../../contexts/UserContext"; // Import the user context
import React, { useState, useEffect } from "react";

const URL = import.meta.env.VITE_API_URL;


export default function Home({ searchQuery, filters }) {
  const { user } = useUser();
  const [vinyls, setVinyls] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  const filterFunction = (vinyls) => {
    return vinyls.filter((vinyl) => {
      console.log(vinyl);
      const albumName = (vinyl.album_name || "").toLowerCase();
      const artist = (vinyl.artist || "").toLowerCase();
      const genre = (vinyl.genre.id || "") ;
      const searchTerm = searchQuery.toLowerCase();
      // Search
      const searchMatch =
        !searchQuery ||
        albumName.includes(searchTerm) ||
        artist.includes(searchTerm);
      // Filters
      const artistMatch =
        !filters.artist || artist.includes(filters.artist.toLowerCase());
      const yearMatch =
        !filters.release_year ||
        vinyl.release_year === parseInt(filters.release_year);
      const genreMatch =
        !filters.genre || genre === parseInt(filters.genre);
      const exchangeMatch =
        !filters.available_for_exchange ||
        vinyl.available_for_exchange === true;
      const coverMatch =
        !filters.cover_condition ||
        vinyl.cover_condition.id === parseInt(filters.cover_condition);
      const recordMatch =
        !filters.record_condition ||
        vinyl.record_condition.id === parseInt(filters.record_condition);

      return (
        searchMatch &&
        artistMatch &&
        yearMatch &&
        genreMatch &&
        exchangeMatch &&
        coverMatch &&
        recordMatch
      );
    });
  };
  // Fetch all vinyls when the component mounts
  useEffect(() => {
    const fetchVinyls = async () => {
      try {
        const response = await fetch(`${URL}/api/records/`, {
          method: "GET",
        });

        if (!response.ok) {
          throw new Error("Failed to fetch vinyls");
        }

        const data = await response.json();
        setVinyls(data);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching vinyls:", error);
        setErrorMessage("Failed to load vinyl records. Please try again.");
        setLoading(false);
      }
    };

    fetchVinyls();
  }, []);

  const filteredVinyls = filterFunction ? filterFunction(vinyls) : vinyls;

  if (loading) {
    return <div>Loading...</div>;
  }

  if (errorMessage) {
    return <div className="error-message">{errorMessage}</div>;
  }
  
  return (
    <div>
      {!user?.username ? (
        <AllVinyls filteredVinyls={filteredVinyls} />
      ) : (
        <>
          <AddVinyl 
            onAddItem={(newItem) => { console.log(newItem); setVinyls((prevVinyls) => [...prevVinyls, newItem])}}
          />
          <AllVinyls filteredVinyls={filteredVinyls} />
        </>
      )}
    </div>
  );  
}
