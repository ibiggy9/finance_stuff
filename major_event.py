import pandas as pd
import numpy as np
from scipy import stats
import seaborn as sns
import matplotlib.pyplot as plt

# Parse the data
data_str = """Dates Cass_Freight Powerfleet Samsara Trimble
2020-01-01	1.022	7.54	23.87	42.52
2020-02-01	1.085	7.05	21.73	39.48
2020-03-01	1.087	3.46	16.19	31.83
2020-04-01	0.923	4.8	19	34.63
2020-05-01	0.938	4.7	23.09	39.12
2020-06-01	0.971	4.62	23.37	43.19
2020-07-01	1.018	4.48	24.38	44.51
2020-08-01	1.099	5.62	28.79	52.41
2020-09-01	1.177	5.63	25.67	48.7
2020-10-01	1.18	6.05	23.11	48.13
2020-11-01	1.154	6.88	29.29	59.87
2020-12-01	1.122	7.43	32.9	66.77
2021-01-01	1.11	7.1	37.04	65.91
2021-02-01	1.13	7.87	36.13	74.14
2021-03-01	1.196	8.22	35.21	77.79
2021-04-01	1.178	7.56	38.63	82
2021-05-01	1.269	6.74	38.44	77.79
2021-06-01	1.231	7.2	40.94	81.83
2021-07-01	1.177	6.81	39.69	85.5
2021-08-01	1.234	7.12	44.07	94.22
2021-09-01	1.184	6.7	41.82	82.25
2021-10-01	1.189	6.92	43.2	87.37
2021-11-01	1.206	6.1	33.53	85.87
2021-12-01	1.208	4.74	29.08	87.19
2022-01-01	1.078	3.57	18.1	72.16
2022-02-01	1.171	3.57	17.48	69.75
2022-03-01	1.203	2.97	16.02	72.14
2022-04-01	1.172	2.64	12.34	66.7
2022-05-01	1.235	2.37	11.25	68.05
2022-06-01	1.203	2.17	11.17	58.23
2022-07-01	1.232	2.75	14.46	69.43
2022-08-01	1.278	3.19	14.87	63.25
2022-09-01	1.241	3.08	12.07	54.27
2022-10-01	1.224	2.65	12.31	60.16
2022-11-01	1.201	2.82	9.53	59.75
2022-12-01	1.161	2.69	12.43	50.56
2023-01-01	1.124	2.86	13.64	58.06
2023-02-01	1.167	2.78	16.66	52.06
2023-03-01	1.155	3.43	19.72	52.42
2023-04-01	1.144	2.87	18.05	47.1
2023-05-01	1.166	3.13	19.25	46.67
2023-06-01	1.147	3	27.71	52.94
2023-07-01	1.122	2.71	27.94	53.8
2023-08-01	1.143	2.46	27.36	54.79
2023-09-01	1.163	2.07	25.21	53.86
2023-10-01	1.108	1.85	23.07	47.13
2023-11-01	1.094	2.32	27.54	46.4
2023-12-01	1.077	3.42	33.38	53.2
2024-01-01	1.039	3.2	31.4	50.86
2024-02-01	1.115	3.17	34.55	61.19
2024-03-01	1.113	5.34	37.79	64.36
2024-04-01	1.098	4.79	34.93	60.07
2024-05-01	1.098	5.31	33.93	55.68
2024-06-01	1.078	4.57	33.7	55.92
2024-07-01	1.11	4.53	38.28	54.54
2024-08-01	1.121	4.99	41.07	56.69
2024-09-01	1.102	5.00	48.12	62.09"""
# Add approximate Fed Funds Rate for these periods
rates_data = {
    '2020-01-01': 1.55,  # Pre-COVID
    '2020-03-01': 0.08,  # Emergency cut
    '2020-06-01': 0.08,  # Zero rate policy
    '2020-12-01': 0.08,  # Zero rate policy
    '2021-05-01': 0.08,  # Zero rate policy
    '2021-10-01': 0.08,  # Zero rate policy
    '2022-01-01': 0.08,  # Just before hikes
    '2022-04-01': 0.33,  # First hikes
    '2022-09-01': 2.33,  # Aggressive hikes
    '2023-02-01': 4.33,  # Peak hiking
    '2023-06-01': 5.08,  # Near peak
    '2024-02-01': 5.33   # Recent peak
}

# Convert to DataFrame
df_rates = pd.DataFrame(list(rates_data.items()), columns=['Date', 'Fed_Rate'])
df_rates['Date'] = pd.to_datetime(df_rates['Date'])

# Parse original data
rows = [row.split() for row in data_str.split('\n')[1:]]
df = pd.DataFrame(rows, columns=['Date', 'Cass_Freight', 'Powerfleet', 'Samsara', 'Trimble'])
df['Date'] = pd.to_datetime(df['Date'])
numeric_cols = ['Cass_Freight', 'Powerfleet', 'Samsara', 'Trimble']
df[numeric_cols] = df[numeric_cols].astype(float)

# Merge with rates
df = pd.merge_asof(df.sort_values('Date'), df_rates.sort_values('Date'), on='Date')

# Define major events/periods
events = {
    'COVID Crash\n(FF: 0.08%)': ('2020-03-01', '2020-05-01'),
    'Recovery Phase\n(FF: 0.08%)': ('2020-06-01', '2020-12-01'),
    'Supply Chain Crisis\n(FF: 0.08%)': ('2021-05-01', '2021-10-01'),
    'Post-Stimulus/Rate Hikes\n(FF: 0.33-2.33%)': ('2022-01-01', '2022-04-01'),
    'Rate Collapse\n(FF: 2.33-4.33%)': ('2022-09-01', '2023-02-01'),
    'Tech Rebound\n(FF: 5.08-5.33%)': ('2023-06-01', '2024-02-01')
}

def analyze_event_period(data, start_date, end_date):
    """Analyze a specific event period with rates context"""
    mask = (data['Date'] >= start_date) & (data['Date'] <= end_date)
    period_data = data[mask]
    
    # Calculate returns and rate change
    total_returns = {}
    for col in numeric_cols:
        start_value = period_data[col].iloc[0]
        end_value = period_data[col].iloc[-1]
        total_returns[col] = ((end_value / start_value) - 1) * 100
    
    rate_change = period_data['Fed_Rate'].iloc[-1] - period_data['Fed_Rate'].iloc[0]
    avg_rate = period_data['Fed_Rate'].mean()
    
    # Calculate correlations with Cass Index
    returns = period_data[numeric_cols].pct_change()
    correlations = {}
    for col in ['Powerfleet', 'Samsara', 'Trimble']:
        correlations[col] = returns['Cass_Freight'].corr(returns[col])
    
    return {
        'returns': total_returns,
        'correlations': correlations,
        'avg_cass': period_data['Cass_Freight'].mean(),
        'rate_change': rate_change,
        'avg_rate': avg_rate
    }

# Analyze each event period
event_analysis = {}
for event_name, (start_date, end_date) in events.items():
    event_analysis[event_name] = analyze_event_period(df, start_date, end_date)

# Print results
print("\nMajor Event Analysis with Interest Rate Context:\n")
for event_name, analysis in event_analysis.items():
    print(f"\n{event_name}")
    print(f"Period Average Cass Index: {analysis['avg_cass']:.3f}")
    print(f"Average Fed Funds Rate: {analysis['avg_rate']:.2f}%")
    print(f"Rate Change During Period: {analysis['rate_change']:.2f}%")
    print("\nTotal Returns:")
    for asset, ret in analysis['returns'].items():
        print(f"{asset}: {ret:.1f}%")
    print("\nCorrelations with Cass Index:")
    for stock, corr in analysis['correlations'].items():
        print(f"{stock}: {corr:.3f}")
    print("-" * 50)