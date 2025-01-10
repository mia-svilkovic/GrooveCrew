import React, { useState, useEffect } from "react";
import "./FilterPanel.css";

const URL = import.meta.env.VITE_API_URL;

const FilterPanel = ({ filters, onFilterChange, handleFilterReset }) => {
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

  if (loading) {
    return <div>Loading filters...</div>;
  }

  if (errorMessage) {
    return <div className="error-message">{errorMessage}</div>;
  }

  return (
    <div className="filter-panel">
      <div className="form-container">
        <h2>Filters</h2>
        <form>
          <input
            type="text"
            name="artist"
            value={filters.artist}
            onChange={handleChange}
            placeholder="Filter by artist"
          />

          <input
            type="number"
            name="release_year"
            value={filters.release_year}
            onChange={handleChange}
            placeholder="Filter by year"
            min="1900"
            max={new Date().getFullYear()}
          />

          <select name="genre" value={filters.genre} onChange={handleChange}>
            <option value="">All Genres</option>
            {genres.map((genre) => (
              <option key={genre.id} value={genre.id}>
                {genre.name}
              </option>
            ))}
          </select>

          <select
            name="cover_condition"
            value={filters.cover_condition}
            onChange={handleChange}
          >
            <option value="">Any Cover Condition</option>
            {coverConditions.map((condition) => (
              <option key={condition.id} value={condition.id}>
                {condition.name}
              </option>
            ))}
          </select>

          <select
            name="record_condition"
            value={filters.record_condition}
            onChange={handleChange}
          >
            <option value="">Any Record Condition</option>
            {recordConditions.map((condition) => (
              <option key={condition.id} value={condition.id}>
                {condition.name}
              </option>
            ))}
          </select>

          <label>
            <input
              type="checkbox"
              name="available_for_exchange"
              checked={filters.available_for_exchange}
              onChange={handleChange}
            />
            Available for Exchange Only
          </label>

          <button type="button" onClick={handleFilterReset}>
            Reset All
          </button>
        </form>
      </div>
    </div>
  );
};
export default FilterPanel;
