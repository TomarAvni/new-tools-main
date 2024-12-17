import pandas as pd
import plotly.graph_objs as go

# Load the datasets
old_data = pd.read_csv(r"C:\Users\prisma\Downloads\psd_data_new.csv")  # replace with the actual path
new_data = pd.read_csv(r"C:\Users\prisma\Downloads\psd_data_old.csv")  # replace with the actual path

# Extract median, mean, and standard deviation columns
old_median = old_data['Median_PSD']
old_std = old_data['Std_PSD']
new_median = new_data['Median_PSD']
new_mean = new_data['Mean_PSD']
new_std = new_data['Std_PSD']

# Generate x-axis values (assuming DOF column represents x-axis)
x_old = old_data['DOF']
x_new = new_data['DOF']

# Plot the old data with median and standard deviation
old_median_trace = go.Scatter(
    x=x_old,
    y=old_median,
    mode='lines',
    name='Old Median',
    line=dict(color='blue', dash='dot')
)

old_std_upper = go.Scatter(
    x=x_old,
    y=old_median + old_std,
    mode='lines',
    name='Old + Std',
    line=dict(color='blue', width=0),
    showlegend=False
)

old_std_lower = go.Scatter(
    x=x_old,
    y=old_median - old_std,
    mode='lines',
    fill='tonexty',
    fillcolor='rgba(173, 216, 230, 0.4)',  # Increased opacity for visibility
    line=dict(color='blue', width=0),
    showlegend=False
)

# Plot the new data with median, mean, and standard deviation
new_median_trace = go.Scatter(
    x=x_new,
    y=new_median,
    mode='lines',
    name='New Median',
    line=dict(color='red', dash='dot')
)

new_mean_trace = go.Scatter(
    x=x_new,
    y=new_mean,
    mode='lines',
    name='New Mean',
    line=dict(color='green')
)

new_std_upper = go.Scatter(
    x=x_new,
    y=new_median + new_std,
    mode='lines',
    name='New + Std',
    line=dict(color='red', width=0),
    showlegend=False
)

new_std_lower = go.Scatter(
    x=x_new,
    y=new_median - new_std,
    mode='lines',
    fill='tonexty',
    fillcolor='rgba(255, 182, 193, 0.4)',  # Increased opacity for visibility
    line=dict(color='red', width=0),
    showlegend=False
)

# Combine all traces
fig = go.Figure(data=[
    old_median_trace, old_std_upper, old_std_lower,
    new_median_trace, new_mean_trace, new_std_upper, new_std_lower
])

# Update layout
fig.update_layout(
    title="Comparison of Old and New Data",
    xaxis_title="DOF",
    yaxis_title="PSD Values",
    template="plotly_white"  # Set to a light theme
)

# Show plot
fig.show()