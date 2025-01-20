import React, { useState } from 'react';
import Offers from '../pages/Offers';

const OffersWrapper = () => {
  const [key, setKey] = useState(0);

  const refreshOffers = () => {
    setKey(prevKey => prevKey + 1);
  };

  return <Offers key={key} onNeedRefresh={refreshOffers} />;
};

export default OffersWrapper;