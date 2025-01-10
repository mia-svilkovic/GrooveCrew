import React from "react";
import "./SearchBar.css";
import searchIcon from "../../assets/images/search.png";
import filterIcon from "../../assets/images/filter.png";

const SearchBar = ({ searchQuery, onSearchChange, onToggleFilters }) => {
  const handleInputChange = (e) => {
    onSearchChange(e.target.value);
  };

  return (
    <div className="search-bar">
      <div className="search-input-container">
        <img src={searchIcon} alt="Search" className="search-icon" />
        <input
          type="text"
          placeholder="Search by album or artist..."
          value={searchQuery}
          onChange={handleInputChange}
          className="search-input"
        />
      </div>
      <button
        className="filter-button"
        onClick={onToggleFilters}
        aria-label="Toggle filters"
      >
        <img src={filterIcon} alt="Filters" className="filter-icon" />
      </button>
    </div>
  );
};

export default SearchBar;
