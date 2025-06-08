import pandas as pd

async def machine_metrics(raw_data):
    df = pd.DataFrame(raw_data)

    datetime_cols = ['Timestamp', 'Downtime Start', 'Downtime End']
    for col in datetime_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce', format="%Y-%m-%d %H:%M:%S")

    opening_time = df['Timestamp'].max() - df['Timestamp'].min()
    required_time = opening_time
    # planned_stop_time = 0 non implémenté

    downtime_df = df.dropna(subset=['Downtime Start', 'Downtime End'])
    unplanned_stop_time = (downtime_df['Downtime End'] - downtime_df['Downtime Start']).sum()
    operating_time = required_time - unplanned_stop_time

    net_time = operating_time
    # cadency_variance = 0 non implémenté

    nok_count = (df['Compliance'] != 'OK').sum()
    useful_time = net_time - pd.Timedelta(seconds=nok_count)

    operating_sec = operating_time.total_seconds()
    net_sec = net_time.total_seconds()
    required_sec = required_time.total_seconds()

    quality_rate = (useful_time / net_time) * 100 if net_time else 0
    operating_rate = (net_sec / operating_sec) * 100 if operating_sec > 0 else 0
    availability_rate = (operating_sec / required_sec) * 100 if required_sec > 0 else 0

    OEE = (quality_rate / 100) * (operating_rate / 100) * (availability_rate / 100) * 100

    downtime_count = len(downtime_df)
    mtbf = operating_time / downtime_count if downtime_count > 0 else pd.Timedelta(0)
    mttr = unplanned_stop_time / downtime_count if downtime_count > 0 else pd.Timedelta(0)

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
        "OEE": OEE,
        "MTBF": str(mtbf),
        "MTTR": str(mttr)
    }

async def fetch_issues(raw_data):
    df = pd.DataFrame(raw_data)
    issues = df[df["Event"] == "Machine Error"]
    return issues[["Timestamp", "Event", "Error Code", "Error Description", "Downtime Start", "Downtime End"]]