import { useState } from 'react'
import './App.css'

function App() {
  const [symbol, setSymbol] = useState('BANKNIFTY')
  const [status, setStatus] = useState('')
  const [loading, setLoading] = useState(false)
  const [marketData, setMarketData] = useState<any>(null)

  const API_URL = 'http://127.0.0.1:5000/api'

  const fetchData = async () => {
    setLoading(true)
    setStatus('Fetching data...')
    setMarketData(null)
    try {
      const response = await fetch(`${API_URL}/market-data/${symbol}?period=3mo`, {
        method: 'GET'
      })
      const data = await response.json()
      if (response.ok) {
        setStatus(`Data fetched successfully for ${data.symbol}. Latest Price: ${data.latest_price}`)
        setMarketData(data)
      } else {
        setStatus(`Error: ${data.error}`)
      }
    } catch (error) {
      setStatus(`Error: ${error}`)
    }
    setLoading(false)
  }

  const generateReport = async () => {
    setLoading(true)
    setStatus('Generating report...')
    try {
      const response = await fetch(`${API_URL}/reports/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ symbol, period: '3mo' })
      })
      const data = await response.json()
      if (response.ok) {
        setStatus(`Report generated successfully! Path: ${data.report_path}`)
      } else {
        setStatus(`Error: ${data.error}`)
      }
    } catch (error) {
      setStatus(`Error: ${error}`)
    }
    setLoading(false)
  }

  return (
    <div className="container">
      <h1>MarketInsight Pro</h1>
      <div className="card">
        <div className="input-group">
          <label>Symbol:</label>
          <input 
            type="text" 
            value={symbol} 
            onChange={(e) => setSymbol(e.target.value)} 
            placeholder="Enter Symbol (e.g. BANKNIFTY)"
          />
        </div>
        <div className="actions">
          <button onClick={fetchData} disabled={loading}>
            {loading ? 'Processing...' : 'Fetch Market Data'}
          </button>
          <button onClick={generateReport} disabled={loading}>
            Generate Report
          </button>
        </div>
        {status && <div className="status-box">{status}</div>}
        
        {marketData && (
          <div className="data-preview">
            <h3>Market Data Preview</h3>
            <p>Latest Close: {marketData.latest_price}</p>
            <p>Last 5 candles:</p>
            <ul>
              {marketData.data.slice(-5).map((candle: any, index: number) => (
                <li key={index}>
                  Date: {candle.Date || index}, Close: {candle.Close?.toFixed(2)}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
