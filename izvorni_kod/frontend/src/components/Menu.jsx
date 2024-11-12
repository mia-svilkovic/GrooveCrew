import React from "react";
import "./Menu.css" ;
import like from "../pictures/like.png"; 
import exchange from "../pictures/exchange.png";
import vinyl from "../pictures/vinyl.png";
import history from "../pictures/history.png";

function Menu({ showMenu }) {
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
          <div className="menu-item">
            <img src={vinyl} alt="vinyl" />
            <span>My vinyls</span>
          </div>
          <div className="menu-item">
            <img src={history} alt="history" />
            <span>History</span>
          </div>
        </div>
      )}
    </div>
  );
}

export default Menu ;
