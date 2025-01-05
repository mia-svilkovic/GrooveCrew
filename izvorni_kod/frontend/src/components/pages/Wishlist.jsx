import React, { useState, useEffect } from "react";
import { useUser } from "../../contexts/UserContext";
import AddButton from "../../assets/images/add.png";
import bin from "../../assets/images/bin.png";
import FormWishlistAdd from "../forms/FormWishlistAdd";
import "./Wishlist.css";

const URL = import.meta.env.VITE_API_URL;

export default function Wishlist() {
  const [wishlist, setWishlist] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");
  const [activeForm, setActiveForm] = useState(null);

  const openAddForm = () => setActiveForm("add");
  const closeForm = () => setActiveForm(null);

  const { user } = useUser();

  const handleRemove = async (wishlistEntry) => {
    const entryId = wishlistEntry["id"];

    try {
      const token = localStorage.getItem("access");

      const response = await fetch(`${URL}/api/wishlist/${entryId}/delete/`, {
        method: "DELETE",
        credentials: "include",
        headers: {
          Authorization: token ? `Bearer ${token}` : "",
        },
      });
      if (!response.ok) {
        throw new Error("Failed to remove item from wishlist");
      }

      setWishlist((prevWishlist) =>
        prevWishlist.filter((item) => item.id !== entryId)
      );
    } catch (error) {
      console.error("Error removing item:", error);
      setErrorMessage("Failed to remove item. Please try again.");
    }
  };

  useEffect(() => {
    const fetchWishlist = async () => {
      try {
        const token = localStorage.getItem("access");

        const response = await fetch(`${URL}/api/wishlist/`, {
          method: "GET",
          credentials: "include",
          headers: {
            Authorization: token ? `Bearer ${token}` : "",
          },
        });

        if (!response.ok) {
          throw new Error("Failed to fetch from wishlist");
        }

        const data = await response.json();
        setWishlist(data);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching vinyls:", error);
        setErrorMessage("Failed to load vinyl records. Please try again.");
        setLoading(false);
      }
    };

    fetchWishlist();
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (errorMessage) {
    return <div className="error-message">{errorMessage}</div>;
  }

  return (
    <div className="wishlist-container">
      <h2>My Wishlist</h2>
      {wishlist.length === 0 ? (
        <p>You don't have anything added to wishlist.</p>
      ) : (
        <div className="wishlist-list">
          {wishlist.map((item) => (
            <div key={item["id"]} className="wishlist-item">
              <p>{item["record_catalog_number"]}</p>
              <button
                className="wishlist-remove"
                onClick={() => handleRemove(item)}
              >
                <img src={bin} alt={bin} />
              </button>
            </div>
          ))}
        </div>
      )}
      <div className="add-container">
        <img
          className="add-button"
          src={AddButton}
          alt="add-button"
          onClick={openAddForm}
        />
        {activeForm === "add" && (
          <div className="modal-overlay">
            <FormWishlistAdd
              onClose={closeForm}
              onAddItem={(newItem) => {
                setWishlist((prevWishlist) => [...prevWishlist, newItem]);
              }}
            />{" "}
          </div>
        )}
      </div>
    </div>
  );
}
