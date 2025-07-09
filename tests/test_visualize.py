from visualize import plot_hosts
import pandas as pd
import matplotlib
# force non‐interactive backend for CI
matplotlib.use('Agg')


def test_plot_hosts(tmp_path):
    # create a tiny CSV
    data = {
        'Network': ['192.168.1.0', '10.0.0.0'],
        'CIDR': ['/24', '/8'],
        'Total Usable Hosts': [254, 16_777_214]
    }
    df = pd.DataFrame(data)
    report_csv = tmp_path / "report.csv"
    chart_png = tmp_path / "chart.png"

    df.to_csv(report_csv, index=False)
    plot_hosts(str(report_csv), str(chart_png))

    assert chart_png.exists()
    # file size should be > 0
    assert chart_png.stat().st_size > 0
