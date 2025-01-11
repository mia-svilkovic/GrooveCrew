import React from 'react';

const Description = ({ value, onChange }) => {
  return (
    <textarea
      name="additional_description"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder="Additional Description"
    />
  );
};

export default Description ;