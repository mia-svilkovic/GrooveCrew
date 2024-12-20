import AddVinyl from "../AddVinyl" ;
import AllVinyls from "../AllVinyls" ;
import { useUser } from "../../contexts/UserContext"; // Import the user context
import React, { useState } from "react";

export default function Home({ searchQuery, filters }) {
  const { user } = useUser();
  
  const filterVinyls = (vinyls) => {
    return vinyls.filter(vinyl => {
      const albumName = (vinyl.album_name || '').toLowerCase();
      const artist = (vinyl.artist || '').toLowerCase();
      const genre = (vinyl.genre || '').toLowerCase();
      const searchTerm = searchQuery.toLowerCase();
      // Search
      const searchMatch = !searchQuery || albumName.includes(searchTerm) ||artist.includes(searchTerm);
      // Filters
      const artistMatch = !filters.artist || artist.includes(filters.artist.toLowerCase());
      const yearMatch = !filters.release_year || vinyl.release_year === parseInt(filters.release_year);
      const genreMatch = !filters.genre || genre === filters.genre.toLowerCase();
      const exchangeMatch = !filters.available_for_exchange || vinyl.available_for_exchange === true;
      const coverMatch = !filters.cover_condition || vinyl.cover_condition === filters.cover_condition;
      const recordMatch = !filters.record_condition || vinyl.record_condition === filters.record_condition;

      return searchMatch && artistMatch && yearMatch && genreMatch && exchangeMatch && coverMatch && recordMatch;
    });
  };
  /*
  const handleVinylAdded = () => {
    setRefreshTrigger(prev => prev + 1);
  };
  */

  if (!user) return (
    <div>
      { <AllVinyls filterFunction={filterVinyls}/> }
    </div>
  ) ;
  return (
    <div>
      <AddVinyl/>
      { <AllVinyls filterFunction={filterVinyls}/> }
    </div>
  );
}
