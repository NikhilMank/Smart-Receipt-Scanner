import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = 'https://jo1dafqlb5.execute-api.eu-central-1.amazonaws.com/prod';

function Profile() {
  const [profile, setProfile] = useState({
    name: '',
    email: '',
    monthly_budget: 0
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const token = localStorage.getItem('id_token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      
      const response = await axios.get(`${API_BASE_URL}/profile`, { headers });
      console.log('Fetched profile data:', response.data);
      setProfile(response.data);
    } catch (error) {
      console.error('Error fetching profile:', error);
      setMessage('Error loading profile');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage('');

    try {
      const token = localStorage.getItem('id_token');
      const headers = {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      };
      
      console.log('Sending profile data:', profile);
      console.log('Request headers:', headers);
      console.log('API URL:', `${API_BASE_URL}/profile`);
      console.log('Request method: PUT');
      console.log('Full axios config:', { method: 'PUT', url: `${API_BASE_URL}/profile`, data: profile, headers });
      
      const response = await axios({
        method: 'PUT',
        url: `${API_BASE_URL}/profile`,
        data: profile,
        headers: headers
      });
      console.log('Profile update response:', response.data);
      setMessage('✅ Profile updated successfully!');
    } catch (error) {
      console.error('Error updating profile:', error);
      console.error('Error details:', error.response?.data);
      setMessage('❌ Error updating profile');
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setProfile(prev => ({
      ...prev,
      [name]: name === 'monthly_budget' ? parseFloat(value) || 0 : value
    }));
  };

  if (loading) {
    return <div className="loading">Loading profile...</div>;
  }

  return (
    <div className="card">
      <h2>👤 Profile Settings</h2>
      
      <form onSubmit={handleSubmit} style={{ marginTop: '20px' }}>
        <div style={{ marginBottom: '15px' }}>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Name:
          </label>
          <input
            type="text"
            name="name"
            value={profile.name}
            onChange={handleChange}
            style={{
              width: '100%',
              padding: '8px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '14px'
            }}
            placeholder="Enter your name"
          />
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Email:
          </label>
          <input
            type="email"
            name="email"
            value={profile.email}
            onChange={handleChange}
            style={{
              width: '100%',
              padding: '8px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '14px'
            }}
            placeholder="Enter your email"
          />
        </div>

        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Monthly Budget (€):
          </label>
          <input
            type="number"
            name="monthly_budget"
            value={profile.monthly_budget}
            onChange={handleChange}
            min="0"
            step="0.01"
            style={{
              width: '100%',
              padding: '8px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '14px'
            }}
            placeholder="Enter your monthly budget"
          />
          <small style={{ color: '#666', fontSize: '12px' }}>
            Set your monthly spending budget to track your expenses
          </small>
        </div>

        <button
          type="submit"
          disabled={saving}
          style={{
            backgroundColor: saving ? '#ccc' : '#2196F3',
            color: 'white',
            padding: '10px 20px',
            border: 'none',
            borderRadius: '4px',
            cursor: saving ? 'not-allowed' : 'pointer',
            fontSize: '14px'
          }}
        >
          {saving ? 'Saving...' : 'Save Profile'}
        </button>
      </form>

      {message && (
        <div style={{
          marginTop: '15px',
          padding: '10px',
          borderRadius: '4px',
          backgroundColor: message.includes('✅') ? '#d4edda' : '#f8d7da',
          color: message.includes('✅') ? '#155724' : '#721c24',
          border: `1px solid ${message.includes('✅') ? '#c3e6cb' : '#f5c6cb'}`
        }}>
          {message}
        </div>
      )}
    </div>
  );
}

export default Profile;