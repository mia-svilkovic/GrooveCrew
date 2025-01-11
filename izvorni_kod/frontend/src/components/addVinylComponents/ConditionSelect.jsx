import React from 'react';

const ConditionSelect = ({ conditions, type, value, onChange }) => {
  const name = `${type.toLowerCase()}_condition_id`;
  return (
    <select
      name={name}
      value={value}
      onChange={onChange}
      required
    >
      <option value="">{type} Condition</option>
      {conditions.map((condition) => (
        <option key={condition.id} value={condition.id}>
          {condition.name}
        </option>
      ))}
    </select>
  );
};

export default ConditionSelect;
