import React from 'react';
import "./Selector.css";

function Selector() {
    
    return(
        <div className='selector-container'>
            <button className='wishlist-button'>Wishlist</button>
            <button className='offers-button'>Offers</button>
            <button className='my-vinyls-button'>My vinyls</button>
            <button className='history-button'>History</button>
        </div>
    );
}

export default Selector