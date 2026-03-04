import { useEffect, useState } from "react";
import { BrowserRouter, Routes, Route, Outlet, useNavigate } from "react-router-dom";
import Navbar from "./components/Navbar";

import HomePage from "./pages/HomePage";
import AdminPage from "./pages/AdminPage";
import NotFoundPage from "./pages/NotFoundPage";

function Layout({ searchValue, setSearchValue, isAuthed, setIsAuthed }) {
  const navigate = useNavigate();

  const onLoginClick = () => navigate("/admin");

  const onLogoutClick = () => {
    localStorage.removeItem("token");
    setIsAuthed(false);
    navigate("/");
  };

  const onCollectClick = () => navigate("/admin");

  return (
    <>
      <Navbar
        searchValue={searchValue}
        onSearch={setSearchValue}
        isAuthed={isAuthed}
        onLoginClick={onLoginClick}
        onLogoutClick={onLogoutClick}
        onCollectClick={onCollectClick}
      />
      <Outlet />
    </>
  );
}

export default function App() {
  const [searchValue, setSearchValue] = useState("");
  const [isAuthed, setIsAuthed] = useState(false);

  useEffect(() => {
    setIsAuthed(Boolean(localStorage.getItem("token")));
  }, []);

  return (
    <BrowserRouter>
      <Routes>
        <Route
          element={
            <Layout
              searchValue={searchValue}
              setSearchValue={setSearchValue}
              isAuthed={isAuthed}
              setIsAuthed={setIsAuthed}
            />
          }
        >
          <Route path="/" element={<HomePage searchValue={searchValue} />} />
          <Route path="/admin" element={<AdminPage isAuthed={isAuthed} setIsAuthed={setIsAuthed} />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}