import React from 'react';
import './FilterPanel.css';

const FilterPanel = ({ filters, onFilterChange }) => {

  const conditions = ['M', 'NM', 'VG', 'G', 'F', 'P'];
  const genres = ['Rock', 'Jazz', 'Classical', 'Pop', 'Hip Hop', 'Electronic', 'Blues', 'Country', 'Folk', 'Other'];
  
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    onFilterChange(name, type === 'checkbox' ? checked : value);
  };

  const handleReset = (e) => {
    // Prevent any default button behavior
    e.preventDefault();
    
    console.log("Reset button clicked");
    console.log("Current filters:", filters);
    
    // Try resetting one filter at a time with small delay
    setTimeout(() => onFilterChange('artist', ''), 0);
    setTimeout(() => onFilterChange('release_year', ''), 50);
    setTimeout(() => onFilterChange('genre', ''), 100);
    setTimeout(() => onFilterChange('available_for_exchange', false), 150);
    setTimeout(() => onFilterChange('cover_condition', ''), 200);
    setTimeout(() => onFilterChange('record_condition', ''), 250);
    
    console.log("Reset attempted");
  };


  return (
    <div className="filter-panel">
      <h3>Filters</h3>

      <div className="filter-section">
        <label>Artist</label>
        <input
          type="text"
          name="artist"
          value={filters.artist}
          onChange={handleChange}
          placeholder="Filter by artist"
        />
      </div>

      <div className="filter-section">
        <label>Release Year</label>
        <input
          type="number"
          name="release_year"
          value={filters.release_year}
          onChange={handleChange}
          placeholder="Filter by year"
          min="1900"
          max={new Date().getFullYear()}
        />
      </div>

      <div className="filter-section">
        <label>Genre</label>
        <select 
          name="genre" 
          value={filters.genre}
          onChange={handleChange}
        >
          <option value="">All Genres</option>
          {genres.map(genre => (
            <option key={genre} value={genre.toLowerCase()}>
              {genre}
            </option>
          ))}
        </select>
      </div>

      <div className="filter-section">
        <label>Cover Condition</label>
        <select
          name="cover_condition"
          value={filters.cover_condition}
          onChange={handleChange}
        >
          <option value="">Any Condition</option>
          {conditions.map(condition => (
            <option key={condition} value={condition}>
              {condition}
            </option>
          ))}
        </select>
      </div>

      <div className="filter-section">
        <label>Record Condition</label>
        <select
          name="record_condition"
          value={filters.record_condition}
          onChange={handleChange}
        >
          <option value="">Any Condition</option>
          {conditions.map(condition => (
            <option key={condition} value={condition}>
              {condition}
            </option>
          ))}
        </select>
      </div>

      <div className="filter-section checkbox">
        <label>
          <input
            type="checkbox"
            name="available_for_exchange"
            checked={filters.available_for_exchange}
            onChange={handleChange}
          />
          Available for Exchange Only
        </label>
      </div>

      {/* <button type="button" onClick={handleReset} className="reset-button">
          Reset All
      </button> */}
    </div>
  );
};

export default FilterPanel;