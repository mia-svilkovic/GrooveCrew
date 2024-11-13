import { useState } from 'react'
import Header from './components/Header.jsx'
import './App.css'
import Authentication from './components/Authentication.jsx'

import AddButton from './pictures/add.png'
import FormAdd from'./components/FormAdd.jsx'

function App() {
  const [activeForm, setActiveForm] = useState(null); // null means no form is open
  const openAddForm = () => setActiveForm("add");
  const closeForm = () => setActiveForm(null);


  return(
    <>
      <Header></Header>
      <div className='add-container'>
        <img className="add-button" src={AddButton} alt="add-button" onClick={openAddForm}/>

        {activeForm === "add" && (
        <div className="modal-overlay">
          <FormAdd onClose={closeForm} />{" "}
        </div>
       )}
      </div>
    
    </>
    
  );
}

export default App
