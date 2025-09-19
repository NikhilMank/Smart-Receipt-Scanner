import React, { useState } from 'react';
import axios from 'axios';

const API_BASE_URL = 'https://jo1dafqlb5.execute-api.eu-central-1.amazonaws.com/prod';

function UploadReceipt({ onUploadSuccess }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');
  const [preview, setPreview] = useState(null);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      
      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => setPreview(e.target.result);
      reader.readAsDataURL(file);
      
      setUploadStatus('');
    }
  };

  const handleCameraCapture = (event) => {
    handleFileSelect(event);
  };

  const uploadFile = async () => {
    if (!selectedFile) {
      setUploadStatus('Please select a file first');
      return;
    }

    setUploading(true);
    setUploadStatus('Getting upload URL...');

    try {
      // Get presigned URL
      const token = localStorage.getItem('id_token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      
      const response = await axios.post(`${API_BASE_URL}/upload/presigned-url`, {
        filename: selectedFile.name,
        contentType: selectedFile.type
      }, { headers });

      const { uploadUrl, key } = response.data;
      setUploadStatus('Uploading file...');

      // Upload file to S3
      await axios.put(uploadUrl, selectedFile, {
        headers: {
          'Content-Type': selectedFile.type
        }
      });

      setUploadStatus('Processing receipt...');
      
      // Wait a moment for Lambda to process
      setTimeout(() => {
        setUploadStatus('✅ Receipt uploaded and processed successfully!');
        setSelectedFile(null);
        setPreview(null);
        if (onUploadSuccess) {
          onUploadSuccess();
        }
      }, 2000);

    } catch (error) {
      console.error('Upload error:', error);
      setUploadStatus('❌ Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const clearSelection = () => {
    setSelectedFile(null);
    setPreview(null);
    setUploadStatus('');
  };

  return (
    <div className="upload-container">
      <div className="card">
        <h2>Upload Receipt</h2>
        
        {/* Upload Options */}
        <div className="upload-options">
          {/* File Upload */}
          <div className="upload-option">
            <label htmlFor="file-upload" className="upload-btn">
              📁 Choose File
            </label>
            <input
              id="file-upload"
              type="file"
              accept="image/*,.pdf"
              onChange={handleFileSelect}
              style={{ display: 'none' }}
            />
          </div>

          {/* Camera Capture (Mobile) */}
          <div className="upload-option">
            <label htmlFor="camera-capture" className="upload-btn camera-btn">
              📷 Take Photo
            </label>
            <input
              id="camera-capture"
              type="file"
              accept="image/*"
              capture="environment"
              onChange={handleCameraCapture}
              style={{ display: 'none' }}
            />
          </div>
        </div>

        {/* File Preview */}
        {preview && (
          <div className="preview-section">
            <h3>Preview:</h3>
            <div className="preview-container">
              <img src={preview} alt="Receipt preview" className="preview-image" />
              <div className="preview-info">
                <p><strong>File:</strong> {selectedFile.name}</p>
                <p><strong>Size:</strong> {(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
                <p><strong>Type:</strong> {selectedFile.type}</p>
              </div>
            </div>
            
            <div className="preview-actions">
              <button onClick={uploadFile} disabled={uploading} className="upload-submit-btn">
                {uploading ? 'Uploading...' : 'Upload & Process'}
              </button>
              <button onClick={clearSelection} className="clear-btn">
                Clear
              </button>
            </div>
          </div>
        )}

        {/* Upload Status */}
        {uploadStatus && (
          <div className={`upload-status ${uploadStatus.includes('✅') ? 'success' : uploadStatus.includes('❌') ? 'error' : 'info'}`}>
            {uploadStatus}
          </div>
        )}

        {/* Instructions */}
        <div className="upload-instructions">
          <h3>Instructions:</h3>
          <ul>
            <li>📱 On mobile: Use "Take Photo" to capture receipt with camera</li>
            <li>💻 On desktop: Use "Choose File" to select image or PDF</li>
            <li>✨ Supported formats: JPG, PNG, PDF</li>
            <li>📊 Receipt will be automatically processed and added to your analytics</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default UploadReceipt;