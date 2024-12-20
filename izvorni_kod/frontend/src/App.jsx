import { BrowserRouter, Routes, Route } from "react-router-dom";
import Header from "./components/Header";
import Home from "./components/pages/Home";
import MyVinyls from "./components/pages/my-vinyls"
import { UserProvider } from "./contexts/UserContext"; // Importiraj UserProvider
import React, { useState } from "react";


function App() {

  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({
    artist: '',
    release_year: '',
    genre: '',
    available_for_exchange: false,
    cover_condition: '',
    record_condition: ''
  });
  const handleSearchAndFilter = (query, filters) => {
    setSearchQuery(query);
    setFilters(filters);
  };

  return (
    <UserProvider>
      <BrowserRouter>
        <div className="app">
          <Header
            filters={filters} 
            searchQuery={searchQuery}
            onSearchAndFilter={handleSearchAndFilter}
          />
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Home searchQuery={searchQuery} filters={filters}/>} />
              <Route path="/my-vinyls" element={<MyVinyls />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </UserProvider>
  );
}

export default App;
