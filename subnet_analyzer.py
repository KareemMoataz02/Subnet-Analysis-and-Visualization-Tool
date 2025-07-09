import argparse
import sys

import pandas as pd
import ipaddress


def analyze_subnets(df: pd.DataFrame) -> pd.DataFrame:
    """
    Given a DataFrame with columns 'IP Address' and 'Subnet Mask',
    return a summary DataFrame with:
      - Network
      - CIDR
      - Total Addresses
      - Total Usable Hosts
    """
    records = []
    for idx, row in df.iterrows():
        ip = row.get('IP Address')
        mask = row.get('Subnet Mask')
        try:
            net = ipaddress.IPv4Network(f"{ip}/{mask}", strict=False)
        except Exception as e:
            print(
                f"Warning: skipping row {idx} ({ip}/{mask}): {e}",
                file=sys.stderr
            )
            continue

        prefix = net.prefixlen
        total_addrs = net.num_addresses
        usable = total_addrs - 2 if prefix <= 30 else total_addrs

        records.append({
            'Network':            str(net.network_address),
            'CIDR':               f"/{prefix}",
            'Total Addresses':    total_addrs,
            'Total Usable Hosts': usable
        })

    if not records:
        return pd.DataFrame(
            columns=['Network', 'CIDR',
                     'Total Addresses', 'Total Usable Hosts']
        )

    summary = (
        pd.DataFrame(records)
          .drop_duplicates(subset=['Network', 'CIDR'])
          .groupby(['Network', 'CIDR'], as_index=False)
          .agg({
              'Total Addresses':    'first',
              'Total Usable Hosts': 'sum'
          })
    )
    return summary


def find_overlaps(nets: list[ipaddress.IPv4Network]) -> list[tuple]:
    overlaps = []
    for i in range(len(nets)):
        for j in range(i + 1, len(nets)):
            if nets[i].overlaps(nets[j]):
                overlaps.append((nets[i], nets[j]))
    return overlaps


def write_report(summary: pd.DataFrame, out_md: str = 'report.md') -> None:
    """
    Generate report.md from the summary DataFrame.
    Q1: Subnet w/ most hosts
    Q2: Any overlaps?
    Q3: Smallest & largest by address space
    Q4: Suggested strategy
    """
    # Q1
    idx_max = summary['Total Usable Hosts'].idxmax()
    row_max = summary.loc[idx_max]

    # Q2: build network objects from summary
    nets = [
        ipaddress.IPv4Network(f"{r.Network}{r.CIDR}", strict=False)
        for r in summary.itertuples()
    ]
    overlaps = find_overlaps(nets)

    # Q3
    idx_min_addr = summary['Total Addresses'].idxmin()
    row_min = summary.loc[idx_min_addr]
    idx_max_addr = summary['Total Addresses'].idxmax()
    row_big = summary.loc[idx_max_addr]

    with open(out_md, 'w') as f:
        f.write('# Analysis Questions\n\n')

        f.write('1. **Which subnet has the most hosts?**  \n')
        f.write(
            f"- `{row_max.Network}{row_max.CIDR}` with "
            f"{row_max['Total Usable Hosts']} usable hosts  \n\n"
        )

        f.write('2. **Are there any overlapping subnets?**  \n')
        if overlaps:
            for a, b in overlaps:
                f.write(
                    f"- `{a.network_address}/{a.prefixlen}` overlaps with "
                    f"`{b.network_address}/{b.prefixlen}`  \n"
                )
        else:
            f.write('- No overlapping subnets found.  \n')
        f.write('\n')

        f.write(
            '3. **What is the smallest and largest subnet in terms of address space?**  \n'
        )
        f.write(
            f"- Smallest: `{row_min.Network}{row_min.CIDR}` "
            f"({row_min['Total Addresses']} total addresses)  \n"
        )
        f.write(
            f"- Largest: `{row_big.Network}{row_big.CIDR}` "
            f"({row_big['Total Addresses']} total addresses)  \n\n"
        )

        f.write(
            '4. **Suggest a subnetting strategy to reduce wasted IPs in this network.**  \n'
        )
        f.write(
            '- Adopt **VLSM** (Variable-Length Subnet Masking) to size each block precisely.  \n')
        f.write('- **Aggregate** contiguous subnets for route summarization.  \n')
        f.write(
            '- **Right-size** any large `/22` into smaller `/23` or `/24` to reclaim unused space.  \n')

    print(f"→ Generated {out_md}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description="Analyze IP/subnet data & auto-generate report"
    )
    p.add_argument(
        "--input", default="ip_data.xlsx",
        help="Excel file with 'IP Address' & 'Subnet Mask' columns"
    )
    p.add_argument(
        "--output", default="subnet_report.csv",
        help="Filename for CSV or JSON summary"
    )
    p.add_argument(
        "--json", action="store_true",
        help="Emit JSON instead of CSV for the summary"
    )
    p.add_argument(
        "--skip-summary", action="store_true",
        help="Do not write the summary file"
    )
    p.add_argument(
        "--skip-report", action="store_true",
        help="Do not generate report.md"
    )
    args = p.parse_args()

    # 1) Read once
    try:
        df = pd.read_excel(args.input)
    except Exception as e:
        print(f"Error: cannot read '{args.input}': {e}", file=sys.stderr)
        sys.exit(1)

    # 2) Build summary DataFrame
    summary = analyze_subnets(df)

    # 3) Optionally write summary
    if not args.skip_summary:
        try:
            if args.json:
                summary.to_json(args.output, orient='records', indent=2)
            else:
                summary.to_csv(args.output, index=False)
            print(f"→ Wrote {len(summary)} rows to {args.output}")
        except Exception as e:
            print(f"Error: failed to write summary: {e}", file=sys.stderr)
            sys.exit(1)

    # 4) Optionally generate the Markdown report
    if not args.skip_report:
        write_report(summary, out_md='report.md')
