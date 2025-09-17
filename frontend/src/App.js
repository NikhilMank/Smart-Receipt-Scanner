import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ReceiptList from './components/ReceiptList';
import Analytics from './components/Analytics';

const API_BASE_URL = 'https://q24kalixmb.execute-api.eu-central-1.amazonaws.com/prod';

function App() {
  const [receipts, setReceipts] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [monthlyTrends, setMonthlyTrends] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('receipts');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [receiptsRes, analyticsRes, trendsRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/receipts`),
        axios.get(`${API_BASE_URL}/analytics/summary`),
        axios.get(`${API_BASE_URL}/analytics/monthly`)
      ]);

      setReceipts(receiptsRes.data.receipts);
      setAnalytics(analyticsRes.data.summary);
      setMonthlyTrends(trendsRes.data.monthly_trends);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="container">
      <div className="header">
        <h1>Receipt Analytics Dashboard</h1>
        <div style={{ marginTop: '10px' }}>
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
            Receipts
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
            Analytics
          </button>
        </div>
      </div>

      {activeTab === 'receipts' && <ReceiptList receipts={receipts} />}
      {activeTab === 'analytics' && (
        <Analytics 
          analytics={analytics} 
          monthlyTrends={monthlyTrends} 
        />
      )}
    </div>
  );
}

export default App;