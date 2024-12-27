import React, { useState, useEffect } from "react";
import "./AllVinyls.css"; // Add your custom styles if needed
import like from "../assets/images/like.png";
import exchange from "../assets/images/exchange.png";

const URL = import.meta.env.VITE_API_URL;

function AllVinyls({filteredVinyls}) {

  return (
    <div className="vinyls-container">
      <div
        className="debug-info"
        style={{ marginBottom: "20px", color: "#666" }}
      >
        <p>results: {filteredVinyls.length}</p>
      </div>
      {filteredVinyls.length === 0 ? (
        <p>No vinyls found.</p>
      ) : (
        <div className="vinyl-list">
          {filteredVinyls.map((vinyl) => (
            <div key={vinyl.id} className="vinyl-item">
              <h3>{vinyl.album_name}</h3>
              <p>Artist: {vinyl.artist}</p>
              <p>Genre: {vinyl.genre.name}</p>
              <p>Location: {vinyl.location}</p>
              <p>
                Available for Exchange:{" "}
                {vinyl.available_for_exchange ? "Yes" : "No"}
              </p>
              <p>Description: {vinyl.additional_description}</p>
              <div>
                <button key={vinyl.id + "exchange"} className="vinyl-opt">
                  <img src={exchange} alt={exchange} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default AllVinyls;
