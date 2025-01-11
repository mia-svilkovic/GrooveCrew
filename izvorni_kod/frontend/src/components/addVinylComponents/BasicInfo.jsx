import React from 'react';

const BasicInfo = ({ formData, onChange }) => {
  return (
    <div>
      <input
        type="text"
        name="catalogNumber"
        placeholder="Catalog Number"
        value={formData.catalogNumber}
        onChange={(e) => onChange(e.target.name, e.target.value)}
        required
      />
      <input
        type="text"
        name="artist"
        placeholder="Artist"
        
        onChange={(e) => onChange(e.target.name, e.target.value)}
        required
      />
      <input
        type="text"
        name="albumName"
        placeholder="Album Name"
        value={formData.album_name}
        onChange={(e) => onChange(e.target.name, e.target.value)}
        required
      />
      <input
        type="number"
        name="releaseYear"
        placeholder="Release Year"
        value={formData.releaseYear}
        onChange={(e) => onChange(e.target.name, e.target.value)}
        min="1900"
        required
      />
    </div>
  );
};

export default BasicInfo;