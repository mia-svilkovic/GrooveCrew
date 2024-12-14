import React from "react";
//import "./MyVinyls.css" ;


function MyVinyls({ vinyls, showVinyls }) {
  return (
    <div>
        {showVinyls && (
        <div className="My_vinyls">
            <h2>My Vinyl Records</h2>
            <ul>
            {vinyls.map(vinyl => (
                <li key={vinyl.release_code} className="vinyl_data">
                    <h3>{vinyl.album_name}</h3>
                    <p>Artist: {vinyl.artist}</p>
                    <p>Genre: {vinyl.genre}</p>
                    <p>Location: {vinyl.location.city}, {vinyl.location.country}</p>
                    <p>Available for Exchange: {vinyl.available_for_exchange ? "Yes" : "No"}</p>
                    <p>Description: {vinyl.additional_description}</p>
                </li>
            ))}
            </ul>
        </div>
        )}
    </div>
  );
}
export default MyVinyls;