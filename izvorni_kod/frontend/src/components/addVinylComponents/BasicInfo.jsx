import React from 'react';

const BasicInfo = ({ formData, onChange }) => {
    const handleChange = (e) => {
        const { name, value } = e.target;
        onChange(name, value);
      
    };
    return (
        <div>
        <input
            type="text"
            name="catalog_number"
            value={formData.catalog_number}
            onChange={onChange}
            placeholder="Catalog Number"
            required
        />
        <input
            type="text"
            name="artist"
            value={formData.artist}
            onChange={onChange}
            placeholder="Artist"
            required
        />
        <input
            type="text"
            name="album_name"
            value={formData.album_name}
            onChange={onChange}
            placeholder="Album Name"
            required
        />
        <input
            type="number"
            name="release_year"
            value={formData.release_year}
            onChange={onChange}
            placeholder="Release Year"
            min="1900"
            required
        />
        </div>
    );
    };

export default BasicInfo;
