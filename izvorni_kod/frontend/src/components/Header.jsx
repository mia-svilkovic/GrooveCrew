import "./Header.css";
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Authentication from "./HeaderComponents/Authentication";
import Menu from "./HeaderComponents/Menu";
import SearchBar from "./HeaderComponents/SearchBar";
import FilterPanel from "./HeaderComponents/FilterPanel";
import logo from "../assets/images/logo.png";
import userIcon from "../assets/images/user.png";
import menuIcon from "../assets/images/menu.png";
import { useUser } from "../contexts/UserContext"; // Uvozimo useUser hook
import FormLogin from './forms/FormLogin';

function Header({ filters, searchQuery, onSearchAndFilter, handleFilterReset }) {
  const [showAuth, setShowAuth] = useState(false);
  const [showMenu, setShowMenu] = useState(false);
  const [showFilters, setShowFilters] = useState(false);

  const [showLoginForm, setShowLoginForm] = useState(false);

  const handleSearch = (query) => {
    onSearchAndFilter(query, filters);
  };
  const handleFilterChange = (key, value) => {
    const newFilters = {
      ...filters,
      [key]: value,
    };
    onSearchAndFilter(searchQuery, newFilters);
  };

  const navigate = useNavigate();

  // Dohvatimo podatke o korisniku iz UserContexta
  const { user } = useUser();
  console.log(user) ;

  const toggleAuth = () => {
    setShowAuth(!showAuth);
    if (showMenu) setShowMenu(false);
  };

  const toggleMenu = () => {
    if (!user?.username) {
      setShowLoginForm(true);
      return;
    }
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
        <button id="menu_button" className="icon-button" onClick={toggleMenu}>
          <img src={menuIcon} alt="Menu" />
        </button>
        <img
          src={logo}
          alt="Logo"
          className="logo"
          onClick={handleLogoClick}
          style={{ cursor: "pointer" }}
        />

        {/* Ako je korisnik prijavljen, prikaži njegovo ime */}
        {user?.username ? (
          <span className="username">user: {user.username}</span>
        ) : null}
        <span className="username">user: username</span>

        <div className="search-container">
          <SearchBar
            searchQuery={searchQuery}
            onSearchChange={handleSearch}
            onToggleFilters={() => setShowFilters(!showFilters)}
          />
          {showFilters && (
            <FilterPanel
              filters={filters}
              onFilterChange={handleFilterChange}
              handleFilterReset={handleFilterReset}
            />
          )}
        </div>

        <button id="auth-button" className="icon-button" onClick={toggleAuth}>
          <img src={userIcon} alt="User" />
        </button>
      </header>

      {showAuth && <Authentication />}
      {showLoginForm && (
        <div className="modal-overlay">
            <FormLogin onClose={() => setShowLoginForm(false)} showMessage={true}/>
        </div>
      )}

      {/* <Menu isOpen={showMenu} /> */}
      <div className="menu-container">
        <Menu isOpen={showMenu} />
      </div>
    </div>
  );
}

export default Header;
