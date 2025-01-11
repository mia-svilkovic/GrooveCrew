import React from 'react';

export const GenreSelect = ({ genres, selectedGenre, onChange }) => {
  return (
    <select
      name="genre"
      value={selectedGenre}
      onChange={(e) => onChange(e.target.value)}
      required
    >
      <option value="">Select Genre</option>
      {genres.map((genre) => (
        <option key={genre.id} value={genre.id}>
          {genre.name}
        </option>
      ))}
    </select>
  );
};

export default GenreSelect;
