const path = require("path");

module.exports = {
  apps: [
    {
      name: "insurminds",
      cwd: __dirname,
      script: path.join(__dirname, ".venv", "Scripts", "python.exe"),
      args: [
        "-m",
        "streamlit",
        "run",
        "app.py",
        "--server.address",
        "127.0.0.1",
        "--server.port",
        "8505",
        "--server.headless",
        "true",
        "--browser.gatherUsageStats",
        "false",
      ],
      interpreter: "none",
      autorestart: true,
      restart_delay: 3000,
      max_restarts: 10,
      min_uptime: "10s",
      time: true,
      env: {
        PYTHONUNBUFFERED: "1",
      },
    },
  ],
};

