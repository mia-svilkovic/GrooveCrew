import { BrowserRouter, Routes, Route } from "react-router-dom";
import Header from "./components/Header";
import Home from "./components/pages/Home";
import MyVinyls from "./components/pages/my-vinyls"
import { UserProvider } from "./contexts/UserContext"; // Importiraj UserProvider

function App() {

  

  return (
    <UserProvider>
      <BrowserRouter>
        <div className="app">
          <Header />
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/my-vinyls" element={<MyVinyls />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </UserProvider>
  );
}

export default App;
