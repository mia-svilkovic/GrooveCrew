import React from 'react';

const PhotoUpload = ({ photoPreviews, onPhotoChange, onRemovePhoto }) => {
  return (
    <div>
      <input
        type="file"
        accept="image/*"
        multiple
        style={{ color: 'transparent' }}
        onChange={onPhotoChange}
      />
      {photoPreviews.length > 0 && (
        <div className="existing-photos">
          <h4>Photos:</h4>
          <div className="photo-grid">
            {photoPreviews.map((preview, index) => (
              <div key={index} className="photo-item">
                <img src={preview} alt="Preview" className="thumbnail" />
                <button
                  type="button"
                  onClick={() => onRemovePhoto(index)}
                  className="remove-photo"
                >
                  Remove
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default PhotoUpload;
