import React from 'react';

const Description = ({ value, onChange }) => {
  return (
    <textarea
      name="additional_description"
      value={value}
      onChange={onChange}
      placeholder="Additional Description"
    />
  );
};

export default Description ;