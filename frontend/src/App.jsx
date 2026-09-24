// frontend/src/App.jsx
import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

function App() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Form states for the ML Predictor
  const [frequency, setFrequency] = useState(5);
  const [totalSpend, setTotalSpend] = useState(500);
  const [avgOrderValue, setAvgOrderValue] = useState(100);
  const [totalItems, setTotalItems] = useState(20);
  const [prediction, setPrediction] = useState(null);
  const [predicting, setPredicting] = useState(false);

  // Fetch KPI & Top Product Analytics on mount
  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/analytics')
      .then((res) => {
        if (!res.ok) throw new Error('API server is offline');
        return res.json();
      })
      .then((data) => {
        setAnalytics(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  // Handle ML Prediction Form Submit
  const handlePredict = async (e) => {
    e.preventDefault();
    setPredicting(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          frequency: intValue(frequency),
          total_spend: floatValue(totalSpend),
          avg_order_value: floatValue(avgOrderValue),
          total_items: intValue(totalItems),
        }),
      });
      const data = await res.json();
      setPrediction(data);
    } catch (err) {
      console.error('Inference failed:', err);
    } finally {
      setPredicting(false);
    }
  };

  const intValue = (val) => parseInt(val) || 0;
  const floatValue = (val) => parseFloat(val) || 0.0;

  if (loading) return <div style={styles.center}><h2>⏳ Fetching Dashboard Data...</h2></div>;
  if (error) return <div style={styles.center}><h2>❌ Error: {error}. Make sure FastAPI is running!</h2></div>;

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h1>🛒 ShopInsight</h1>
        <p>E-Commerce Intelligence & ML Prediction Platform</p>
      </header>

      {/* --- KPI SECTION --- */}
      <section style={styles.kpiGrid}>
        <div style={styles.kpiCard}>
          <span style={styles.kpiLabel}>Total Revenue</span>
          <h2 style={styles.kpiValue}>${analytics.kpis.total_revenue.toLocaleString()}</h2>
        </div>
        <div style={styles.kpiCard}>
          <span style={styles.kpiLabel}>Total Orders</span>
          <h2 style={styles.kpiValue}>{analytics.kpis.total_orders.toLocaleString()}</h2>
        </div>
        <div style={styles.kpiCard}>
          <span style={styles.kpiLabel}>Unique Customers</span>
          <h2 style={styles.kpiValue}>{analytics.kpis.unique_customers.toLocaleString()}</h2>
        </div>
        <div style={styles.kpiCard}>
          <span style={styles.kpiLabel}>Avg Order Value</span>
          <h2 style={styles.kpiValue}>${analytics.kpis.avg_order_value}</h2>
        </div>
      </section>

      <hr style={styles.separator} />

      {/* --- MAIN CONTENT GRID --- */}
      <div style={styles.mainGrid}>
        {/* Left: Product Chart */}
        <div style={styles.card}>
          <h2 style={styles.cardTitle}>📈 Top 5 Best-Selling Products ($)</h2>
          <div style={{ height: '300px', marginTop: '20px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={analytics.top_products}>
                <XAxis dataKey="product" tick={{ fill: '#6b7280', fontSize: 10 }} />
                <YAxis tick={{ fill: '#6b7280' }} />
                <Tooltip formatter={(value) => `$${value.toLocaleString()}`} />
                <Bar dataKey="revenue" fill="#4f46e5" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Right: ML Predictor */}
        <div style={styles.card}>
          <h2 style={styles.cardTitle}>🧠 Real-Time Churn Predictor</h2>
          <p style={styles.subtitle}>Enter metrics below to calculate if a customer is likely to stop ordering.</p>
          
          <form onSubmit={handlePredict} style={styles.form}>
            <div style={styles.inputGroup}>
              <label style={styles.label}>Frequency (Total Orders):</label>
              <input type="number" style={styles.input} value={frequency} onChange={e => setFrequency(e.target.value)} required />
            </div>
            <div style={styles.inputGroup}>
              <label style={styles.label}>Total Spend ($):</label>
              <input type="number" step="0.01" style={styles.input} value={totalSpend} onChange={e => setTotalSpend(e.target.value)} required />
            </div>
            <div style={styles.inputGroup}>
              <label style={styles.label}>Average Order Value ($):</label>
              <input type="number" step="0.01" style={styles.input} value={avgOrderValue} onChange={e => setAvgOrderValue(e.target.value)} required />
            </div>
            <div style={styles.inputGroup}>
              <label style={styles.label}>Total Items Purchased:</label>
              <input type="number" style={styles.input} value={totalItems} onChange={e => setTotalItems(e.target.value)} required />
            </div>
            
            <button type="submit" style={styles.button} disabled={predicting}>
              {predicting ? "Calculating..." : "Calculate Churn Probability"}
            </button>
          </form>

          {prediction && (
            <div style={{
              ...styles.predictionBox,
              borderColor: prediction.churn_risk === 'HIGH' ? '#f87171' : '#4ade80',
              backgroundColor: prediction.churn_risk === 'HIGH' ? '#fef2f2' : '#f0fdf4'
            }}>
              <h3>Risk Level: <strong style={{ color: prediction.churn_risk === 'HIGH' ? '#dc2626' : '#16a34a' }}>{prediction.churn_risk}</strong></h3>
              <p style={{ margin: '8px 0' }}>Probability of Churning: <strong>{prediction.probability}%</strong></p>
              <p style={styles.recText}>{prediction.recommendation}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// Inline CSS Styles for absolute ease of setup
const styles = {
  container: { maxWidth: '1200px', margin: '0 auto', padding: '40px 20px', fontFamily: 'system-ui, sans-serif', color: '#1f2937' },
  header: { textAlign: 'center', marginBottom: '40px' },
  separator: { border: '0', height: '1px', background: '#e5e7eb', margin: '40px 0' },
  kpiGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '20px' },
  kpiCard: { background: '#ffffff', padding: '24px', borderRadius: '12px', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05)', border: '1px solid #f3f4f6' },
  kpiLabel: { color: '#6b7280', fontSize: '14px', fontWeight: '500' },
  kpiValue: { fontSize: '28px', margin: '8px 0 0 0', fontWeight: '700', color: '#111827' },
  mainGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(450px, 1fr))', gap: '30px' },
  card: { background: '#ffffff', padding: '30px', borderRadius: '16px', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.05)', border: '1px solid #f3f4f6' },
  cardTitle: { fontSize: '20px', margin: '0 0 10px 0', fontWeight: '600' },
  subtitle: { color: '#6b7280', fontSize: '14px', marginBottom: '20px' },
  form: { display: 'grid', gap: '15px' },
  inputGroup: { display: 'flex', flexDirection: 'column', gap: '5px' },
  label: { fontSize: '13px', fontWeight: '500', color: '#4b5563' },
  input: { padding: '10px', borderRadius: '8px', border: '1px solid #d1d5db', fontSize: '14px' },
  button: { padding: '12px', background: '#4f46e5', color: '#fff', border: 'none', borderRadius: '8px', fontWeight: '600', cursor: 'pointer', transition: 'background 0.2s' },
  predictionBox: { marginTop: '25px', padding: '20px', borderRadius: '12px', borderLeft: '6px solid' },
  recText: { fontSize: '13px', color: '#4b5563', lineHeight: '1.5', margin: '0' },
  center: { display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', fontFamily: 'system-ui, sans-serif' }
};

export default App;
