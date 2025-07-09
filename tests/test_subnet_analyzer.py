import pandas as pd
import ipaddress
from subnet_analyzer import analyze_subnets, find_overlaps, write_report


def sample_df():
    return pd.DataFrame({
        'IP Address': ['192.168.1.10', '192.168.1.20', '10.0.0.5'],
        'Subnet Mask': ['255.255.255.0', '255.255.255.0', '255.0.0.0']
    })


def test_analyze_subnets_unique():
    df = sample_df()
    summary = analyze_subnets(df)

    # We expect exactly two distinct networks
    assert len(summary) == 2
    nets = set(summary['Network'] + summary['CIDR'])
    assert '192.168.1.0/24' in nets
    assert '10.0.0.0/8' in nets

    # Check values for the /24
    row24 = summary[summary['Network'] == '192.168.1.0'].iloc[0]
    assert row24['Total Addresses'] == 256
    assert row24['Total Usable Hosts'] == 254

    # Check values for the /8
    row8 = summary[summary['Network'] == '10.0.0.0'].iloc[0]
    assert row8['Total Addresses'] == 16_777_216
    assert row8['Total Usable Hosts'] == 16_777_214


def test_find_overlaps():
    nets = [
        ipaddress.IPv4Network('192.168.0.0/24'),
        ipaddress.IPv4Network('192.168.0.128/25'),
        ipaddress.IPv4Network('10.0.0.0/8'),
    ]
    overlaps = find_overlaps(nets)

    # Only the first two overlap
    assert len(overlaps) == 1
    a, b = overlaps[0]
    assert {a, b} == {nets[0], nets[1]}


def test_write_report(tmp_path):
    summary = analyze_subnets(sample_df())
    out = tmp_path / "report.md"
    write_report(summary, out_md=str(out))
    content = out.read_text()

    # Basic smoke checks
    assert "# Analysis Questions" in content
    assert "Which subnet has the most hosts?" in content
    assert "10.0.0.0/8" in content
