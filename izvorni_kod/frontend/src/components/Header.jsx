import "./Header.css";
import React, { useState } from "react";
import Authentication from "./Authentication";
import Menu from "./Menu";
import logo from "../pictures/logo.png";
import user from "../pictures/user.png";
import menu from "../pictures/menu.png";


function Header() {
  const [showAuth, setShowAuth] = useState(false);
  const [showMenu, setShowMenu] = useState(false);

  const toggleAuth = () => setShowAuth((prev) => !prev);
  const toggleMenu = () => setShowMenu((prev) => !prev);

  return (
    <div className="container">
      <header className="header-container">
        <img src={menu} alt="menu" onClick={toggleMenu}/>
        <img src={logo} alt="logo" />
        <img src={user} alt="user" onClick={toggleAuth} />
      </header>
      <div className="auth-container">
        {showAuth && <Authentication />}
      </div>
      
      <div className="menu-container"><Menu showMenu={showMenu} /></div>
      

    </div>
  );
}

export default Header
