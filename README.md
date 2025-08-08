# Binary Signal Bot with Admin Dashboard

This is a fully functional trading signal bot system that includes:

- Live scanning of at least 30 currency pairs using:
  - Alligator Indicator
  - EMA-150
  - Stochastic (14, 3, 3) with 70/30 overbought/oversold lines
  - Optional Fractal oscillator
  - Momentum candle detection
  - Volatility filter
  - Historical price pattern checks using 30–50 previous candles
  - Optional Heikin Ashi candle support
- A Flask-based web dashboard for:
  - Viewing trade signals (1-min, 2-min, 3-min, and 5-min timeframes)
  - Selecting/approving trades
  - Sending signals to Telegram only upon approval
  - Managing multiple users with role permissions (Admin/User)
  - Admin-only access to user management (add/remove/authorize users)
- Telegram alerts with:
  - Symbol
  - Direction (Buy/Sell)
  - Timeframe
  - Timestamp

## Features

- 24/7 scanning for Forex OTC and Crypto OTC symbols
- Signal accuracy optimized for 90–95%
- Admin login alerts prepared (via Gmail)
- Render + Railway CLI + UptimeRobot hosting support
- Deployable using Termux

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
