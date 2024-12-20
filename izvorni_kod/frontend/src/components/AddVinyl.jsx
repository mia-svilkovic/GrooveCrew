import FormAdd from'./forms/FormAdd.jsx'
import { useState, useEffect } from 'react'
import AddButton from '../assets/images/add.png'

const URL = import.meta.env.VITE_API_URL;

const gStand = [
  {id: 0, name: 'mint',abbreviation: 'M'},
  {id: 1, name: 'near mint',abbreviation: 'NM'},
  {id: 2, name: 'exellent',abbreviation: 'E'},
  {id: 3, name: 'very good',abbreviation: 'VG'},
  {id: 4, name: 'good',abbreviation: 'G'},
  {id: 5, name: 'poor',abbreviation: 'P'},
];


export default function AddVinyl({onVinylAdded}){
    const [activeForm, setActiveForm] = useState(null); // null means no form is open
    //const [gStand, setGStand] = useState([]);
    //const [loading, setLoading] = useState(true);

    const openAddForm = () => setActiveForm("add");
    const closeForm = () => {
      setActiveForm(null)
      if (onVinylAdded) {
        onVinylAdded();
      }
    };
    /*
    useEffect(() => {
        const fetchGoldmineConditions = async () => {
          try {
            const response = await fetch(`${URL}/api/goldmine-conditions/`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
           
            const data = await response.json();
            setGStand(data); // Update gStand state with fetched data
            setLoading(false); // Set loading to false after data is fetched
          } catch (error) {
            console.error('Error fetching data:', error);
            setGStand([]); // Set to empty array in case of an error
            setLoading(false); // Stop loading even on error
          }
        };
    
        fetchGoldmineConditions(); // Fetch data when the component mounts
      }, []); // Empty dependency array to run only on mount    
      */
    
    return(
        <div className='add-container'>
            <img className="add-button" src={AddButton} alt="add-button" onClick={openAddForm}/>

            {activeForm === "add" && (
            <div className="modal-overlay">
            <FormAdd onClose={closeForm} gStand={gStand}/>{" "}
            </div>
            )}
      </div>
    )
}