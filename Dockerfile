FROM python:3.11-slim

WORKDIR /app

# 1) Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) Copy source files and input template
COPY ip_data.xlsx subnet_analyzer.py visualize.py ./

# 3) Default command: run analysis (generates CSV + MD), then chart
ENTRYPOINT ["/bin/bash", "-lc", "\
    python subnet_analyzer.py --input ip_data.xlsx --output subnet_report.csv && \
    python visualize.py --input subnet_report.csv --output network_plot.png \
    "]

# 4) Expose the output files
VOLUME ["/app"]


