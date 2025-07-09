# visualize.py

import argparse
import pandas as pd
import matplotlib.pyplot as plt


def plot_hosts(report_csv, output_png):
    df = pd.read_csv(report_csv)
    labels = df['Network'] + df['CIDR']
    hosts = df['Total Usable Hosts']

    plt.figure(figsize=(10, 6))
    plt.bar(labels, hosts)
    plt.xticks(rotation=45, ha='right')
    plt.ylabel('Usable Hosts')
    plt.title('Hosts per Subnet')
    plt.tight_layout()
    plt.savefig(output_png)
    print(f"→ Saved chart to {output_png}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input",  required=True, help="Path to subnet_report.csv")
    p.add_argument("--output", required=True,
                   help="Path to write network_plot.png")
    args = p.parse_args()
    plot_hosts(args.input, args.output)
