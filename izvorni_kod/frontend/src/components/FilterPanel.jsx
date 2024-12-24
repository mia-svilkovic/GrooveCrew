import React, { useState, useEffect } from "react";
import "./FilterPanel.css";

const URL = import.meta.env.VITE_API_URL;

const FilterPanel = ({ filters, onFilterChange }) => {
  const [genres, setGenres] = useState([]);
  const [coverConditions, setCoverConditions] = useState([]);
  const [recordConditions, setRecordConditions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  // Fetch genres, cover conditions, and record conditions from backend
  useEffect(() => {
    const fetchFilterData = async () => {
      try {
        const [
          genresResponse,
          coverConditionsResponse,
          recordConditionsResponse,
        ] = await Promise.all([
          fetch(`${URL}/api/genres/`),
          fetch(`${URL}/api/goldmine-conditions-cover/`),
          fetch(`${URL}/api/goldmine-conditions-record/`),
        ]);

        if (
          !genresResponse.ok ||
          !coverConditionsResponse.ok ||
          !recordConditionsResponse.ok
        ) {
          throw new Error("Failed to fetch filter data");
        }

        const [genresData, coverConditionsData, recordConditionsData] =
          await Promise.all([
            genresResponse.json(),
            coverConditionsResponse.json(),
            recordConditionsResponse.json(),
          ]);

        setGenres(genresData);
        setCoverConditions(coverConditionsData);
        setRecordConditions(recordConditionsData);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching filter data:", error);
        setErrorMessage("Failed to load filter data. Please try again.");
        setLoading(false);
      }
    };

    fetchFilterData();
  }, []);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    onFilterChange(name, type === "checkbox" ? checked : value);
  };

  const handleReset = (e) => {
    e.preventDefault();
    onFilterChange("artist", "");
    onFilterChange("release_year", "");
    onFilterChange("genre", "");
    onFilterChange("available_for_exchange", false);
    onFilterChange("cover_condition", "");
    onFilterChange("record_condition", "");
  };

  if (loading) {
    return <div>Loading filters...</div>;
  }

  if (errorMessage) {
    return <div className="error-message">{errorMessage}</div>;
  }

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
        <select name="genre" value={filters.genre} onChange={handleChange}>
          <option value="">All Genres</option>
          {genres.map((genre) => (
            <option key={genre.id} value={genre.id}>
              {genre.name}
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
          {coverConditions.map((condition) => (
            <option key={condition.id} value={condition.id}>
              {condition.name}
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
          {recordConditions.map((condition) => (
            <option key={condition.id} value={condition.id}>
              {condition.name}
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

      <button type="button" onClick={handleReset} className="reset-button">
        Reset All
      </button>
    </div>
  );
};

export default FilterPanel;
