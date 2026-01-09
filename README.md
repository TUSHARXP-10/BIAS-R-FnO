# BIAS-R-FnO: Automated Trading Report Generator

A sophisticated, automated trading report generator that creates comprehensive technical analysis reports for Indian stock market indices (SENSEX, BANKNIFTY, NIFTY50) with GitHub Actions integration for daily report generation.

## 📋 Features

- **Daily Automated Reports**: GitHub Actions workflow generates fresh reports every day at 1:30 PM IST
- **Comprehensive Technical Analysis**: Includes RSI, MACD, Bollinger Bands, EMA, ATR, ADX, and more
- **Actionable Trading Plans**: Clear BUY/SELL/NO TRADE recommendations with entry/exit levels
- **Risk Assessment**: Detailed risk analysis with volatility metrics and position sizing guidance
- **Professional PDF Reports**: Well-formatted, visually appealing reports with embedded charts
- **Signal Tracking**: Built-in signal tracking system for accuracy validation
- **Web UI**: User-friendly frontend for on-demand report generation

## 📊 Reports Generated

- **SENSEX**: Daily technical analysis and trading signals
- **BANKNIFTY**: Comprehensive derivatives market analysis
- **NIFTY50**: Index performance and trading opportunities

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/TUSHARXP-10/BIAS-R-FnO.git
   cd BIAS-R-FnO
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd ../frontend
   npm install
   ```

### Running Locally

1. **Start the backend server**
   ```bash
   cd backend
   python main.py
   ```

2. **Start the frontend development server**
   ```bash
   cd ../frontend
   npm run dev
   ```

3. **Access the application**
   Open your browser and navigate to `http://localhost:5173`

## 🤖 GitHub Actions Workflow

The repository includes a daily GitHub Actions workflow that:

- Runs every day at 9:00 AM UTC (1:30 PM IST)
- Generates reports for all three indices
- Commits and pushes reports to the `reports` directory
- Can be manually triggered for on-demand reports

## 📁 Repository Structure

```
BIAS-R-FnO/
├── backend/                 # Python backend
│   ├── app/                 # Application code
│   │   ├── api/             # API endpoints
│   │   └── services/        # Core services
│   ├── generate_reports.py  # Standalone report generator
│   └── requirements.txt     # Python dependencies
├── frontend/                # React/TypeScript frontend
├── reports/                 # Generated PDF reports
├── charts/                  # Chart images
└── .github/workflows/       # GitHub Actions workflows
```

## 🎯 Usage

### Generate Reports Manually

```bash
cd backend
python generate_reports.py
```

### Access Historical Reports

All generated reports are stored in the `reports` directory. You can browse them directly in the GitHub repository.

## 🛠️ Technologies Used

- **Backend**: Python, Flask, TA-Lib, ReportLab, Pandas
- **Frontend**: React, TypeScript, Vite
- **Automation**: GitHub Actions
- **Data**: Yahoo Finance API

## 📄 License

MIT License

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Contact

For any inquiries or issues, please open an issue on the GitHub repository.

---

*Automated trading reports generated daily with GitHub Actions*