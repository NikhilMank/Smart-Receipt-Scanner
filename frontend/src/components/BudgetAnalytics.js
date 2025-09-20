import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = 'https://jo1dafqlb5.execute-api.eu-central-1.amazonaws.com/prod';

function BudgetAnalytics() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [monthFilter, setMonthFilter] = useState('');

  useEffect(() => {
    fetchAnalytics();
  }, [monthFilter]);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('id_token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      
      const params = monthFilter ? { month_filter: monthFilter } : {};
      const response = await axios.get(`${API_BASE_URL}/analytics/summary`, { 
        headers,
        params
      });
      
      console.log('Analytics response:', response.data);
      setAnalytics(response.data.summary);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderBudgetVisualization = () => {
    console.log('Analytics data:', analytics);
    console.log('Budget value:', analytics?.budget, 'Type:', typeof analytics?.budget);
    console.log('Budget check:', !analytics || analytics.budget <= 0);
    
    if (!analytics || !analytics.budget || analytics.budget <= 0) {
      return (
        <div style={{ 
          padding: '20px', 
          textAlign: 'center', 
          backgroundColor: '#f8f9fa',
          borderRadius: '8px',
          border: '2px dashed #dee2e6'
        }}>
          <p style={{ margin: 0, color: '#6c757d' }}>
            💡 Set a monthly budget in your profile to see budget tracking
          </p>
        </div>
      );
    }

    const budgetUsed = analytics.budget_used || 0;
    const budget = analytics.budget || 0;
    const remaining = Math.max(0, budget - budgetUsed);
    const usedPercentage = Math.min(100, (budgetUsed / budget) * 100);
    
    const categoryColors = {
      grocery: '#28a745',
      restaurant: '#fd7e14',
      clothing: '#e83e8c',
      electronics: '#6f42c1',
      drogerie: '#20c997',
      gas_station: '#ffc107',
      other: '#6c757d'
    };

    return (
      <div>
        <h3>💰 Budget Overview</h3>
        
        {/* Budget Progress Bar */}
        <div style={{ marginBottom: '20px' }}>
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            marginBottom: '8px',
            fontSize: '14px'
          }}>
            <span>Used: €{budgetUsed.toFixed(2)}</span>
            <span>Budget: €{budget.toFixed(2)}</span>
          </div>
          
          <div style={{
            width: '100%',
            height: '30px',
            backgroundColor: '#e9ecef',
            borderRadius: '15px',
            overflow: 'hidden',
            position: 'relative'
          }}>
            <div style={{
              width: `${usedPercentage}%`,
              height: '100%',
              backgroundColor: usedPercentage > 90 ? '#dc3545' : usedPercentage > 75 ? '#ffc107' : '#28a745',
              transition: 'width 0.3s ease'
            }} />
            <div style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              color: usedPercentage > 50 ? 'white' : 'black',
              fontWeight: 'bold',
              fontSize: '12px'
            }}>
              {usedPercentage.toFixed(1)}%
            </div>
          </div>
          
          <div style={{ 
            textAlign: 'center', 
            marginTop: '8px',
            fontSize: '14px',
            color: remaining > 0 ? '#28a745' : '#dc3545'
          }}>
            {remaining > 0 ? `€${remaining.toFixed(2)} remaining` : `€${Math.abs(remaining).toFixed(2)} over budget`}
          </div>
        </div>

        {/* Category Breakdown */}
        <h4>📊 Spending by Category</h4>
        <div style={{ marginBottom: '20px' }}>
          {Object.entries(analytics.by_category || {}).map(([category, amount]) => {
            const percentage = budget > 0 ? (amount / budget) * 100 : 0;
            const color = categoryColors[category] || categoryColors.other;
            
            return (
              <div key={category} style={{ marginBottom: '10px' }}>
                <div style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  marginBottom: '4px',
                  fontSize: '13px'
                }}>
                  <span style={{ textTransform: 'capitalize' }}>{category}</span>
                  <span>€{amount.toFixed(2)} ({percentage.toFixed(1)}%)</span>
                </div>
                <div style={{
                  width: '100%',
                  height: '8px',
                  backgroundColor: '#e9ecef',
                  borderRadius: '4px',
                  overflow: 'hidden'
                }}>
                  <div style={{
                    width: `${Math.min(100, percentage)}%`,
                    height: '100%',
                    backgroundColor: color,
                    transition: 'width 0.3s ease'
                  }} />
                </div>
              </div>
            );
          })}
        </div>

        {/* Budget Status */}
        <div style={{
          padding: '15px',
          borderRadius: '8px',
          backgroundColor: usedPercentage > 90 ? '#f8d7da' : usedPercentage > 75 ? '#fff3cd' : '#d1ecf1',
          border: `1px solid ${usedPercentage > 90 ? '#f5c6cb' : usedPercentage > 75 ? '#ffeaa7' : '#bee5eb'}`
        }}>
          <strong>
            {usedPercentage > 100 ? '⚠️ Over Budget!' : 
             usedPercentage > 90 ? '🚨 Budget Almost Exceeded' :
             usedPercentage > 75 ? '⚡ Approaching Budget Limit' :
             '✅ Within Budget'}
          </strong>
          <p style={{ margin: '5px 0 0 0', fontSize: '13px' }}>
            {usedPercentage > 100 ? 
              `You've exceeded your budget by €${Math.abs(remaining).toFixed(2)}` :
              `You have €${remaining.toFixed(2)} left to spend this period`
            }
          </p>
        </div>
      </div>
    );
  };

  if (loading) {
    return <div className="loading">Loading analytics...</div>;
  }

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>📈 Budget Analytics</h2>
        
        <select 
          value={monthFilter} 
          onChange={(e) => setMonthFilter(e.target.value)}
          style={{
            padding: '8px 12px',
            border: '1px solid #ddd',
            borderRadius: '4px',
            fontSize: '14px'
          }}
        >
          <option value="">All Time</option>
          <option value="this_month">This Month</option>
          <option value="last_month">Last Month</option>
        </select>
      </div>

      {analytics ? renderBudgetVisualization() : (
        <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
          No spending data available
        </div>
      )}
    </div>
  );
}

export default BudgetAnalytics;