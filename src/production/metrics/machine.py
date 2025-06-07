import pandas as pd
import json
import os

def machine_metrics(raw_data):
    """
    Calculate machine efficiency metrics from raw production data.
    :param raw_data: collection of raw production data containing timestamps, downtime, and compliance information.
    :return: a dictionary with calculated metrics including opening time, required time, unplanned stop time, operating time, net time, useful time, quality rate, operating rate, availability rate, TRS (Total Resource Score), MTBF (Mean Time Between Failures), and MTTR (Mean Time To Repair).
    """
    df = pd.DataFrame(raw_data)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df['Downtime Start'] = pd.to_datetime(df['Downtime Start'], format="%Y-%m-%d %H:%M:%S", errors='coerce')
    df['Downtime End'] = pd.to_datetime(df['Downtime End'], format="%Y-%m-%d %H:%M:%S", errors='coerce')

    opening_time = df['Timestamp'].max() - df['Timestamp'].min()        # Calculate opening time
    planned_stop_time = pd.Timedelta(0)                                 # Planned stop time (not implemented)
    required_time = opening_time - planned_stop_time

    downtime_df = df.dropna(subset=['Downtime Start', 'Downtime End'])                              # Create a subset for calculating unplanned stop time
    unplanned_stop_time = (downtime_df['Downtime End'] - downtime_df['Downtime Start']).sum()       # Calculate unplanned stop time
    operating_time = required_time - unplanned_stop_time                                            # Operating time

    cadency_variance = pd.Timedelta(0)                  # Cadency variance (not implemented)
    net_time = operating_time - cadency_variance        # Net time

    nok_time = df[df['Compliance'] != 'OK']['Timestamp'].count()        # Time NOK (non-compliant)
    useful_time = net_time - pd.Timedelta(seconds=nok_time)             # Useful time

    total_parts = df['Part ID'].count()                                         # Compliance metrics
    compliant_parts = df[df['Compliance'] == 'OK']['Compliance'].count()

    quality_rate = (compliant_parts / total_parts) * 100            # Quality rate
    operating_rate = (net_time / operating_time) * 100              # Operating rate
    availability_rate = (operating_time / required_time) * 100      # Availability rate

    # Overall Equipment Effectiveness (OEE)
    TRS = (quality_rate / 100) * (operating_rate / 100) * (availability_rate / 100) * 100

    # Mean Time Between Failures (MTBF)
    if len(downtime_df) > 0:
        mtbf = operating_time / len(downtime_df)
    else:
        mtbf = pd.Timedelta(0)

    # Mean Time To Repair (MTTR)
    if len(downtime_df) > 0:
        mttr = unplanned_stop_time / len(downtime_df)
    else:
        mttr = pd.Timedelta(0)

    return {
        "opening_time": str(opening_time),
        "required_time": str(required_time),
        "unplanned_stop_time": str(unplanned_stop_time),
        "operating_time": str(operating_time),
        "net_time": str(net_time),
        "useful_time": str(useful_time),
        "quality_rate": quality_rate,
        "operating_rate": operating_rate,
        "availability_rate": availability_rate,
        "TRS": TRS,
        "MTBF": str(mtbf),
        "MTTR": str(mttr)
    }

def fetch_issues(raw_data):
    df = pd.DataFrame(raw_data)
    issues = df[df["Event"] == "Machine Error"]
    return issues[["Timestamp", "Event", "Error Code", "Error Description", "Downtime Start", "Downtime End"]]