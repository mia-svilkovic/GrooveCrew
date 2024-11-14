import React from "react";
import "./Menu.css" ;
import like from "../pictures/like.png"; 
import exchange from "../pictures/exchange.png";
import vinyl from "../pictures/vinyl.png";
import history from "../pictures/history.png";
import MyVinyls from "./MyVinyls";
import { useState } from "react";


URL = "http://localhost:8000";

function Menu({ showMenu }) {
  const [vinyls, setVinyls] = useState([]);  
  const [showVinyls, setShowVinyls] = useState(false); 

  const handleMyVinylsClick = async () => {
    if (showVinyls) {
      setShowVinyls(false);  
      return;
    }
    try {
      const response = await fetch(URL + "/fetch_records", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch vinyl records");
      }

      const data = await response.json();
      setVinyls(data);
      setShowVinyls(true);
    } catch (error) {
      console.error("Error fetching vinyl records:", error);
    }
  };

  //testWithoutFetch sluzi da se testira jeli se ploče ispravno pokazuju na frontendu bez pokretanja backenda
  //za koristenje s backendom koristiiti handleMyVinylsClick
  const testWithoutFetch = () => { 
    if (showVinyls) {
      setShowVinyls(false);  
      return;
    }
    const data=
    [{
        "release_code": "VYN1234",
        "artist": "The Beatles",
        "album_name": "Abbey Road",
        "release_year": 1969,
        "genre": "Rock",
        "location": {
          "city": "London",
          "country": "UK"
        },
        "available_for_exchange": true,
        "additional_description": "A classic album in good condition."
    }];
    setVinyls(data);
    setShowVinyls(true);
  }

  return (
    <div>
      {showMenu && (
        <div className="menu-bar">
          <div className="menu-item">
            <img src={like} alt="like" />
            <span>Wishlist</span>
          </div>
          <div className="menu-item">
            <img src={exchange} alt="exchange" />
            <span>Offers</span>
          </div>
          <div className="menu-item" onClick={testWithoutFetch}>

            <img src={vinyl} alt="vinyl" />
            <span>My vinyls</span>
          </div>
          <div className="menu-item">
            <img src={history} alt="history" />
            <span>History</span>
          </div>
        </div>
      )}
      <div>
        <MyVinyls vinyls={vinyls} showVinyls={showVinyls}/>
      </div>
    </div>
  );
}

export default Menu;
