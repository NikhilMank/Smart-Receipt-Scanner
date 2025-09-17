import React, { useState, useEffect } from 'react';
import { 
  PieChart, Pie, Cell, BarChart, Bar, LineChart, Line, 
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from 'recharts';
import axios from 'axios';

const COLORS = [
  '#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8',
  '#82CA9D', '#FFC658', '#FF7C7C', '#8DD1E1', '#D084D0',
  '#87D068', '#FFB347', '#B19CD9', '#FFD700', '#FF6B6B'
];

const API_BASE_URL = 'https://q24kalixmb.execute-api.eu-central-1.amazonaws.com/prod';

function EnhancedAnalytics() {
  const [analytics, setAnalytics] = useState(null);
  const [monthlyTrends, setMonthlyTrends] = useState([]);
  const [receipts, setReceipts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    dateRange: 'all',
    category: 'all',
    customStartDate: '',
    customEndDate: ''
  });

  useEffect(() => {
    fetchData();
  }, [filters]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const params = {};
      
      // Handle custom date range filter
      if (filters.customStartDate && filters.customEndDate) {
        params.start_date = filters.customStartDate;
        params.end_date = filters.customEndDate;
      } else if (filters.dateRange !== 'all') {
        const endDate = new Date();
        const startDate = new Date();
        
        switch (filters.dateRange) {
          case '30days':
            startDate.setDate(endDate.getDate() - 30);
            break;
          case '3months':
            startDate.setMonth(endDate.getMonth() - 3);
            break;
          case '6months':
            startDate.setMonth(endDate.getMonth() - 6);
            break;
          case '1year':
            startDate.setFullYear(endDate.getFullYear() - 1);
            break;
        }
        
        params.start_date = startDate.toISOString().split('T')[0];
        params.end_date = endDate.toISOString().split('T')[0];
      }

      if (filters.category !== 'all') {
        params.category = filters.category;
      }

      const [receiptsRes, analyticsRes, trendsRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/receipts`, { params }),
        axios.get(`${API_BASE_URL}/analytics/summary`, { params }),
        axios.get(`${API_BASE_URL}/analytics/monthly`, { params })
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

  const calculateMetrics = () => {
    if (!receipts.length) return {};

    const amounts = receipts.map(r => parseFloat(r.total_amount?.replace(',', '.') || 0));
    const avgSpending = amounts.reduce((a, b) => a + b, 0) / amounts.length;
    const maxSpending = Math.max(...amounts);
    const merchants = receipts.reduce((acc, r) => {
      acc[r.merchant] = (acc[r.merchant] || 0) + 1;
      return acc;
    }, {});
    const topMerchant = Object.entries(merchants).sort((a, b) => b[1] - a[1])[0];

    return {
      avgSpending: avgSpending.toFixed(2),
      maxSpending: maxSpending.toFixed(2),
      topMerchant: topMerchant ? topMerchant[0] : 'N/A',
      totalTransactions: receipts.length
    };
  };

  const getTopMerchants = () => {
    const merchantTotals = receipts.reduce((acc, receipt) => {
      const merchant = receipt.merchant || 'Unknown';
      const amount = parseFloat(receipt.total_amount?.replace(',', '.') || 0);
      acc[merchant] = (acc[merchant] || 0) + amount;
      return acc;
    }, {});

    return Object.entries(merchantTotals)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([merchant, amount]) => ({ merchant, amount: amount.toFixed(2) }));
  };

  const getAllCategories = () => {
    const categories = new Set();
    monthlyTrends.forEach(month => {
      Object.keys(month)
        .filter(key => !['month', 'total_amount', 'receipt_count'].includes(key))
        .forEach(category => categories.add(category));
    });
    return Array.from(categories);
  };



  const getFilterTitle = () => {
    if (filters.customStartDate && filters.customEndDate) {
      return `Analytics: ${filters.customStartDate} to ${filters.customEndDate}`;
    }
    if (filters.dateRange !== 'all') {
      const rangeLabels = {
        '30days': 'Last 30 Days',
        '3months': 'Last 3 Months', 
        '6months': 'Last 6 Months',
        '1year': 'Last Year'
      };
      return `Analytics: ${rangeLabels[filters.dateRange] || filters.dateRange}`;
    }
    return 'Analytics Overview: All Time';
  };

  if (loading) {
    return <div className="loading">Loading enhanced analytics...</div>;
  }

  if (!analytics) {
    return <div>No analytics data available</div>;
  }

  const metrics = calculateMetrics();
  const topMerchants = getTopMerchants();
  const categories = getAllCategories();
  
  const categoryData = Object.entries(analytics.by_category).map(([category, amount]) => ({
    name: category,
    value: amount
  }));

  return (
    <div>
      {/* Filters */}
      <div className="card" style={{ marginBottom: '20px' }}>
        <h2>Filters</h2>
        <div style={{ display: 'flex', gap: '20px', marginTop: '15px', flexWrap: 'wrap' }}>
          <div>
            <label>Date Range: </label>
            <select 
              value={filters.dateRange} 
              onChange={(e) => setFilters({...filters, dateRange: e.target.value})}
              style={{ padding: '5px', marginLeft: '10px' }}
            >
              <option value="all">All Time</option>
              <option value="30days">Last 30 Days</option>
              <option value="3months">Last 3 Months</option>
              <option value="6months">Last 6 Months</option>
              <option value="1year">Last Year</option>
            </select>
          </div>
          
          <div>
            <label>Date Range: </label>
            <select 
              value={filters.dateRange} 
              onChange={(e) => {
                setFilters({...filters, dateRange: e.target.value, customStartDate: '', customEndDate: ''});
              }}
              style={{ padding: '5px', marginLeft: '10px' }}
            >
              <option value="all">All Time</option>
              <option value="30days">Last 30 Days</option>
              <option value="3months">Last 3 Months</option>
              <option value="6months">Last 6 Months</option>
              <option value="1year">Last Year</option>
              <option value="custom">Custom Range</option>
            </select>
          </div>
          
          {filters.dateRange === 'custom' && (
            <>
              <div>
                <label>From: </label>
                <input 
                  type="date" 
                  value={filters.customStartDate}
                  onChange={(e) => setFilters({...filters, customStartDate: e.target.value})}
                  style={{ padding: '5px', marginLeft: '10px' }}
                />
              </div>
              <div>
                <label>To: </label>
                <input 
                  type="date" 
                  value={filters.customEndDate}
                  onChange={(e) => setFilters({...filters, customEndDate: e.target.value})}
                  style={{ padding: '5px', marginLeft: '10px' }}
                />
              </div>
            </>
          )}
          
          <div>
            <label>Category: </label>
            <select 
              value={filters.category} 
              onChange={(e) => setFilters({...filters, category: e.target.value})}
              style={{ padding: '5px', marginLeft: '10px' }}
            >
              <option value="all">All Categories</option>
              {Object.keys(analytics.by_category || {}).map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>
          
          {(filters.dateRange !== 'all' || filters.category !== 'all') && (
            <button 
              onClick={() => setFilters({dateRange: 'all', category: 'all', customStartDate: '', customEndDate: ''})}
              style={{ padding: '5px 15px', backgroundColor: '#f44336', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
            >
              Clear Filters
            </button>
          )}
        </div>
      </div>

      {/* Title */}
      <div className="card" style={{ textAlign: 'center', marginBottom: '20px' }}>
        <h1 style={{ margin: 0, color: '#333' }}>{getFilterTitle()}</h1>
        {(filters.dateRange !== 'all' || filters.category !== 'all') && (
          <p style={{ margin: '10px 0 0 0', color: '#666' }}>
            Showing filtered results for the selected period and criteria
          </p>
        )}
      </div>

      {/* Key Metrics Cards */}
      <div className="grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)', marginBottom: '20px' }}>
        <div className="card" style={{ textAlign: 'center' }}>
          <h3>Total Spending</h3>
          <p style={{ fontSize: '24px', color: '#2196F3', fontWeight: 'bold' }}>
            €{analytics.total_amount}
          </p>
        </div>
        <div className="card" style={{ textAlign: 'center' }}>
          <h3>Avg per Receipt</h3>
          <p style={{ fontSize: '24px', color: '#4CAF50', fontWeight: 'bold' }}>
            €{metrics.avgSpending}
          </p>
        </div>
        <div className="card" style={{ textAlign: 'center' }}>
          <h3>Highest Purchase</h3>
          <p style={{ fontSize: '24px', color: '#FF9800', fontWeight: 'bold' }}>
            €{metrics.maxSpending}
          </p>
        </div>
        <div className="card" style={{ textAlign: 'center' }}>
          <h3>Top Merchant</h3>
          <p style={{ fontSize: '18px', color: '#9C27B0', fontWeight: 'bold' }}>
            {metrics.topMerchant}
          </p>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid">
        {/* Pie Chart */}
        <div className="card">
          <h2>Spending by Category</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={categoryData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: €${value}`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {categoryData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Top Merchants */}
        <div className="card">
          <h2>Top Merchants</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={topMerchants}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="merchant" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="amount" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Monthly Trends - Stacked */}
        <div className="card" style={{ gridColumn: '1 / -1' }}>
          <h2>Monthly Trends by Category</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={monthlyTrends}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Legend />
              {categories.map((category, index) => (
                <Bar 
                  key={category} 
                  dataKey={category} 
                  stackId="a" 
                  fill={COLORS[index % COLORS.length]} 
                  name={category}
                />
              ))}
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Spending Trend Line */}
        <div className="card" style={{ gridColumn: '1 / -1' }}>
          <h2>Spending Trend Over Time</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={monthlyTrends}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="total_amount" 
                stroke="#8884d8" 
                strokeWidth={3}
                name="Total Spending"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

export default EnhancedAnalytics;