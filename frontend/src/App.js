import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ReceiptList from './components/ReceiptList';
import Analytics from './components/Analytics';
import EnhancedAnalytics from './components/EnhancedAnalytics';
import UploadReceipt from './components/UploadReceipt';
import Auth from './components/Auth';

const API_BASE_URL = 'https://jo1dafqlb5.execute-api.eu-central-1.amazonaws.com/prod';

function App() {
  const [receipts, setReceipts] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [monthlyTrends, setMonthlyTrends] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('upload');
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('id_token');
    if (token) {
      setIsAuthenticated(true);
      fetchData();
    } else {
      setLoading(false);
    }
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('id_token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      
      const [receiptsRes, analyticsRes, trendsRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/receipts`, { headers }),
        axios.get(`${API_BASE_URL}/analytics/summary`, { headers }),
        axios.get(`${API_BASE_URL}/analytics/monthly`, { headers })
      ]);

      setReceipts(receiptsRes.data.receipts);
      setAnalytics(analyticsRes.data.summary);
      setMonthlyTrends(trendsRes.data.monthly_trends);
    } catch (error) {
      console.error('Error fetching data:', error);
      if (error.response?.status === 401) {
        handleLogout();
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = (token) => {
    setIsAuthenticated(true);
    fetchData();
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('id_token');
    setIsAuthenticated(false);
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Auth onLogin={handleLogin} />;
  }

  return (
    <div className="container">
      <div className="header">
        <h1>Receipt Analytics Dashboard</h1>
        <div style={{ marginTop: '10px' }}>
          <button 
            onClick={() => setActiveTab('upload')}
            style={{ 
              marginRight: '10px', 
              padding: '8px 16px',
              backgroundColor: activeTab === 'upload' ? '#2196F3' : '#f0f0f0',
              color: activeTab === 'upload' ? 'white' : 'black',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            📤 Upload
          </button>
          <button 
            onClick={() => setActiveTab('receipts')}
            style={{ 
              marginRight: '10px', 
              padding: '8px 16px',
              backgroundColor: activeTab === 'receipts' ? '#2196F3' : '#f0f0f0',
              color: activeTab === 'receipts' ? 'white' : 'black',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            📄 Receipts
          </button>
          <button 
            onClick={() => setActiveTab('analytics')}
            style={{ 
              padding: '8px 16px',
              backgroundColor: activeTab === 'analytics' ? '#2196F3' : '#f0f0f0',
              color: activeTab === 'analytics' ? 'white' : 'black',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            📊 Analytics
          </button>
          <button 
            onClick={handleLogout}
            style={{ 
              marginLeft: 'auto',
              padding: '8px 16px',
              backgroundColor: '#f44336',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Logout
          </button>
        </div>
      </div>

      {activeTab === 'upload' && <UploadReceipt onUploadSuccess={fetchData} />}
      {activeTab === 'receipts' && <ReceiptList receipts={receipts} />}
      {activeTab === 'analytics' && <EnhancedAnalytics />}
    </div>
  );
}

export default App;