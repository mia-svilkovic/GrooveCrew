import React from "react";
import { useNavigate } from "react-router-dom";
import "./Menu.css";
import like from "../assets/images/like.png";
import exchange from "../assets/images/exchange.png";
import vinyl from "../assets/images/vinyl.png";
import history from "../assets/images/history.png";
import { useUser } from "../contexts/UserContext"; // Import the user context

const MENU_ITEMS = [
  { icon: like, label: "Wishlist", path: "/wishlist" },
  { icon: exchange, label: "Offers", path: "/offers" },
  { icon: vinyl, label: "My vinyls", path: "/my-vinyls" },
  { icon: history, label: "History", path: "/history" },
];

function Menu({ isOpen }) {
  const navigate = useNavigate();
  const { user } = useUser(); // Get user data from context

  // If no user is logged in, return null to hide the menu
  if (!user) {
    return null; // This will prevent the Menu from being rendered
  }

  const handleMenuClick = (path) => {
    navigate(path);
  };

  return (
    <div>
      {isOpen && (
        <div className="menu-bar">
          {MENU_ITEMS.map((item, index) => (
            <button
              key={index}
              className="menu-item"
              onClick={() => handleMenuClick(item.path)}
            >
              <img src={item.icon} alt={item.label} />
              <span>{item.label}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default Menu;
