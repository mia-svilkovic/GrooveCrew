import FormAdd from "./forms/FormAdd.jsx";
import { useState, useEffect } from "react";
import AddButton from "../assets/images/add.png";

const URL = import.meta.env.VITE_API_URL;

export default function AddVinyl({ onVinylAdded }) {
  const [activeForm, setActiveForm] = useState(null); // Tracks active modal state
  const [recordConditions, setRecordConditions] = useState([]);
  const [coverConditions, setCoverConditions] = useState([]);
  const [genres, setGenres] = useState([]); // Add state for genres
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  const openAddForm = () => setActiveForm("add");
  const closeForm = () => setActiveForm(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [recordResponse, coverResponse, genresResponse] =
          await Promise.all([
            fetch(`${URL}/api/goldmine-conditions-record/`, {
              credentials: "include",
            }),
            fetch(`${URL}/api/goldmine-conditions-cover/`, {
              credentials: "include",
            }),
            fetch(`${URL}/api/genres/`, {
              credentials: "include",
            }),
          ]);

        if (!recordResponse.ok || !coverResponse.ok || !genresResponse.ok) {
          throw new Error(`Failed to fetch one or both conditions`);
        }

        const [recordData, coverData, genresData] = await Promise.all([
          recordResponse.json(),
          coverResponse.json(),
          genresResponse.json(),
        ]);

        setRecordConditions(recordData);
        setCoverConditions(coverData);
        setGenres(genresData);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching data:", error);
        setErrorMessage("Failed to load conditions. Please try again.");
        setRecordConditions([]);
        setCoverConditions([]);
        setGenres([]);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return <div>Loading conditions and genres...</div>;
  }

  if (errorMessage) {
    return <div className="error-message">{errorMessage}</div>;
  }

  return (
    <div className="add-container">
      <img
        className="add-button"
        src={AddButton}
        alt="Add Vinyl"
        onClick={openAddForm}
      />

      {activeForm === "add" && (
        <div className="modal-overlay">
          <FormAdd
            onClose={closeForm}
            recordConditions={recordConditions}
            coverConditions={coverConditions}
            genres={genres}
          />
        </div>
      )}
    </div>
  );
}
