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

const API_BASE_URL = 'https://jo1dafqlb5.execute-api.eu-central-1.amazonaws.com/prod';

function EnhancedAnalytics() {
  const [analytics, setAnalytics] = useState(null);
  const [monthlyTrends, setMonthlyTrends] = useState([]);
  const [receipts, setReceipts] = useState([]);
  const [keyMetrics, setKeyMetrics] = useState(null);
  const [spendingPatterns, setSpendingPatterns] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
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
      if (filters.dateRange === 'custom' && filters.customStartDate && filters.customEndDate) {
        params.start_date = filters.customStartDate;
        params.end_date = filters.customEndDate;
      } else if (filters.dateRange !== 'all' && filters.dateRange !== 'custom') {
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

      // Fetch core analytics first
      const token = localStorage.getItem('id_token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      
      const [receiptsRes, analyticsRes, trendsRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/receipts`, { params, headers }),
        axios.get(`${API_BASE_URL}/analytics/summary`, { params, headers }),
        axios.get(`${API_BASE_URL}/analytics/monthly`, { params, headers })
      ]);

      setReceipts(receiptsRes.data.receipts);
      setAnalytics(analyticsRes.data.summary);
      setMonthlyTrends(trendsRes.data.monthly_trends);

      // Try to fetch advanced analytics, but don't fail if they're not available
      try {
        const [metricsRes, patternsRes] = await Promise.all([
          axios.get(`${API_BASE_URL}/analytics/metrics`, { params, headers }),
          axios.get(`${API_BASE_URL}/analytics/patterns`, { params, headers })
        ]);
        setKeyMetrics(metricsRes.data.metrics);
        setSpendingPatterns(patternsRes.data.patterns);
      } catch (advancedError) {
        console.warn('Advanced analytics not available:', advancedError);
        // Calculate basic metrics from receipts as fallback
        if (receiptsRes.data.receipts.length > 0) {
          const amounts = receiptsRes.data.receipts.map(r => parseFloat(r.total_amount?.replace(',', '.') || 0));
          const avgSpending = amounts.reduce((a, b) => a + b, 0) / amounts.length;
          const maxReceipt = receiptsRes.data.receipts.reduce((max, r) => {
            const amount = parseFloat(r.total_amount?.replace(',', '.') || 0);
            return amount > parseFloat(max.total_amount?.replace(',', '.') || 0) ? r : max;
          });
          const merchants = receiptsRes.data.receipts.reduce((acc, r) => {
            acc[r.merchant] = (acc[r.merchant] || 0) + 1;
            return acc;
          }, {});
          const topMerchant = Object.entries(merchants).sort((a, b) => b[1] - a[1])[0];
          
          setKeyMetrics({
            average_spending: avgSpending.toFixed(2),
            most_expensive: {
              amount: parseFloat(maxReceipt.total_amount?.replace(',', '.') || 0).toFixed(2),
              merchant: maxReceipt.merchant || '',
              date: maxReceipt.purchase_date || ''
            },
            most_frequent_merchant: {
              name: topMerchant ? topMerchant[0] : '',
              count: topMerchant ? topMerchant[1] : 0
            },
            month_comparison: {
              current: 0,
              previous: 0,
              change_percent: 0
            }
          });
        }
      }
    } catch (error) {
      console.error('Error fetching data:', error);
      setError('Failed to load analytics data. Please try again.');
    } finally {
      setLoading(false);
    }
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
    return (
      <div className="loading" style={{ textAlign: 'center', padding: '40px' }}>
        <div style={{ fontSize: '18px', marginBottom: '10px' }}>Loading analytics...</div>
        <div style={{ color: '#666' }}>Fetching your receipt data and generating insights</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error" style={{ textAlign: 'center', padding: '40px' }}>
        <div style={{ fontSize: '18px', color: '#e74c3c', marginBottom: '10px' }}>{error}</div>
        <button 
          onClick={() => { setError(null); fetchData(); }}
          style={{ padding: '10px 20px', backgroundColor: '#2196F3', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
        >
          Retry
        </button>
      </div>
    );
  }

  if (!analytics) {
    return <div>No analytics data available</div>;
  }
  
  // Don't show no data message for custom range without dates selected
  if (filters.dateRange === 'custom' && (!filters.customStartDate || !filters.customEndDate)) {
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
          </div>
        </div>
        <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
          <h3>Please select a date range to view analytics</h3>
        </div>
      </div>
    );
  }

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
      <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', marginBottom: '20px' }}>
        <div className="card" style={{ textAlign: 'center' }}>
          <h3>Total Spending</h3>
          <p style={{ fontSize: '24px', color: '#2196F3', fontWeight: 'bold' }}>
            €{analytics.total_amount}
          </p>
        </div>
        <div className="card" style={{ textAlign: 'center' }}>
          <h3>Total Receipts</h3>
          <p style={{ fontSize: '24px', color: '#4CAF50', fontWeight: 'bold' }}>
            {analytics.total_receipts}
          </p>
        </div>
        {keyMetrics && (
          <>
            <div className="card" style={{ textAlign: 'center' }}>
              <h3>Avg per Receipt</h3>
              <p style={{ fontSize: '24px', color: '#FF9800', fontWeight: 'bold' }}>
                €{keyMetrics.average_spending}
              </p>
            </div>
            <div className="card" style={{ textAlign: 'center' }}>
              <h3>Most Expensive</h3>
              <p style={{ fontSize: '20px', color: '#e74c3c', fontWeight: 'bold' }}>
                €{keyMetrics.most_expensive.amount}
              </p>
              <p style={{ fontSize: '12px', color: '#666' }}>{keyMetrics.most_expensive.merchant}</p>
            </div>
            <div className="card" style={{ textAlign: 'center' }}>
              <h3>Top Merchant</h3>
              <p style={{ fontSize: '18px', color: '#9C27B0', fontWeight: 'bold' }}>
                {keyMetrics.most_frequent_merchant.name}
              </p>
              <p style={{ fontSize: '14px', color: '#666' }}>{keyMetrics.most_frequent_merchant.count} visits</p>
            </div>
            <div className="card" style={{ textAlign: 'center' }}>
              <h3>Month vs Previous</h3>
              <p style={{ fontSize: '20px', fontWeight: 'bold', color: keyMetrics.month_comparison.change_percent >= 0 ? '#e74c3c' : '#27ae60' }}>
                {keyMetrics.month_comparison.change_percent >= 0 ? '+' : ''}{keyMetrics.month_comparison.change_percent}%
              </p>
              <p style={{ fontSize: '12px', color: '#666' }}>€{keyMetrics.month_comparison.current} vs €{keyMetrics.month_comparison.previous}</p>
            </div>
          </>
        )}
      </div>

      {/* Charts Grid */}
      <div className="grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
        {/* Pie Chart */}
        <div className="card">
          <h2>Spending by Category</h2>
          {categoryData.length > 0 ? (
            <ResponsiveContainer width="100%" height={350}>
              <PieChart>
                <Pie
                  data={categoryData}
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {categoryData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value, name) => [`€${value}`, name]} />
                <Legend formatter={(value, entry) => `${value}: €${entry.payload.value}`} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div style={{ height: '350px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#666' }}>
              No category data available
            </div>
          )}
        </div>

        {/* Top Merchants */}
        <div className="card">
          <h2>Top Merchants</h2>
          {topMerchants.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={topMerchants}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="merchant" angle={-45} textAnchor="end" height={80} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="amount" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div style={{ height: '300px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#666' }}>
              No merchant data available
            </div>
          )}
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

        {/* Advanced Analytics */}
        {spendingPatterns && (
          <>
            <div className="card">
              <h2>Weekday vs Weekend</h2>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={[
                  { name: 'Weekdays', total: spendingPatterns.weekday_vs_weekend.weekday_total, avg: spendingPatterns.weekday_vs_weekend.weekday_avg },
                  { name: 'Weekends', total: spendingPatterns.weekday_vs_weekend.weekend_total, avg: spendingPatterns.weekday_vs_weekend.weekend_avg }
                ]}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="total" fill="#8884d8" name="Total" />
                  <Bar dataKey="avg" fill="#82ca9d" name="Average" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="card">
              <h2>Spending Forecast</h2>
              <div style={{ textAlign: 'center', padding: '40px' }}>
                <h3>Next Month Prediction</h3>
                <p style={{ fontSize: '32px', color: '#2196F3', fontWeight: 'bold', margin: '20px 0' }}>
                  €{spendingPatterns.prediction.next_month_forecast}
                </p>
                <p style={{ color: '#666' }}>Based on {spendingPatterns.prediction.based_on_months} months average</p>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default EnhancedAnalytics;