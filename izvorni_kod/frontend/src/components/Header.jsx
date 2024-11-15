import "./Header.css";
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Authentication from "./Authentication";
import Menu from "./Menu";
import logo from "../assets/images/logo.png";
import userIcon from "../assets/images/user.png";
import menuIcon from "../assets/images/menu.png";
import { useUser } from "../contexts/UserContext"; // Uvozimo useUser hook

function Header() {
  const [showAuth, setShowAuth] = useState(false);
  const [showMenu, setShowMenu] = useState(false);
  const navigate = useNavigate();

  // Dohvatimo podatke o korisniku iz UserContexta
  const { user } = useUser();

  const toggleAuth = () => {
    setShowAuth(!showAuth);
    if (showMenu) setShowMenu(false);
  };

  const toggleMenu = () => {
    setShowMenu(!showMenu);
    if (showAuth) setShowAuth(false);
  };

  const handleLogoClick = () => {
    navigate("/");
    if (showMenu) setShowMenu(false);
    if (showAuth) setShowAuth(false);
  };

  return (
    <div className="container">
      <header className="header-container">
        <img src={menuIcon} alt="Menu" onClick={toggleMenu} />
        <img
          src={logo}
          alt="Logo"
          className="logo"
          onClick={handleLogoClick}
          style={{ cursor: "pointer" }}
        />

        {/* Ako je korisnik prijavljen, prikaži njegovo ime */}
        {user?.username ? (
          <span className="username">Prijavljeni ste kao:{user.username}</span>
        ) : null}

        <img src={userIcon} alt="User" onClick={toggleAuth} />
      </header>

      {showAuth && <Authentication />}

      <div className="menu-container">
        <Menu isOpen={showMenu} />
      </div>
    </div>
  );
}

export default Header;
