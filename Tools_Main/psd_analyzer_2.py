import sys
sys.path.append(r'C:\Users\prisma\pz\microservices')
import numpy as np
import plotly.graph_objects as go
import pandas as pd
import os
from datetime import timedelta
from pzpy.recording import Recording
import argparse
from plotly.io import to_html


class PSDAnalyzer:
    def __init__(self, recording_path, td_seconds=1, low_freq=1, high_freq=30, n=1800, smoothing_window=50):
        self.recording_path = recording_path
        self.td = timedelta(seconds=td_seconds)
        self.low_freq = low_freq
        self.high_freq = high_freq
        self.rec = Recording.open_recording(recording_path)
        self.total_start_time = self.rec.metadata.start_time
        self.n = n
        self.current_start_time = self.total_start_time
        self.current_end_time = self.total_start_time + self.td
        self.fs = self.rec.metadata.prr
        self.n_samples = self.rec.metadata.num_samples_per_trace
        self.smoothing_window = smoothing_window
        self.psd_data_list = []
        self.dofs_data_list = []

    def moving_average(self, data, window_size):
        return np.convolve(data, np.ones(window_size)/window_size, mode='valid')

    def process(self, export_csv=True, csv_file_path=''):
        fig = go.Figure()

        while self.current_end_time < self.rec.metadata.end_time:
            print('starting...')
            mat = self.rec.get_matrix(time_start=self.current_start_time, time_end=self.current_end_time)
            fft_result = np.fft.fft(mat, axis=0)
            freqs = np.fft.fftfreq(mat.shape[0], d=1 / self.fs)
            psd_matrix = np.abs(fft_result) ** 2
            freq_indices = np.where((freqs >= self.low_freq) & (freqs <= self.high_freq))[0]
            new_math = psd_matrix[freq_indices, :] / freqs[freq_indices][:, np.newaxis]
            mean_psd_values_per_dof_dB = 10 * np.log10(np.mean(new_math, axis=0)) * 2
            print('step 1')

            print(f"max - {np.max(mean_psd_values_per_dof_dB)}")
            print(f"min - {np.min(mean_psd_values_per_dof_dB)}")

            # Apply smoothing (this part remains unchanged)
            smoothed_psd = self.moving_average(mean_psd_values_per_dof_dB, self.smoothing_window)
            dofs = self.rec.metadata.dx * np.arange(len(smoothed_psd))

            # Store results and prepare for plotting
            self.psd_data_list.append(smoothed_psd)
            self.dofs_data_list.append(dofs)

            fig.add_trace(go.Scatter(x=dofs, y=smoothed_psd, mode='lines', name=f"PSD {self.current_start_time}"))

            # Move to next time window
            self.current_start_time += self.n * self.td
            self.current_end_time = self.current_start_time + self.td
            print('step 2')

        # Calculating average, median, and std deviations
        psd_data_array = np.array(self.psd_data_list)
        mean_psd = np.mean(psd_data_array, axis=0)
        std_psd = np.std(psd_data_array, axis=0)
        median_psd = np.median(psd_data_array, axis=0)

        # Average dofs for plotting
        avg_dofs = self.dofs_data_list[0]
        fig.add_trace(
            go.Scatter(x=avg_dofs, y=mean_psd, mode='lines', name="Average PSD", line=dict(color='black', dash='dash')))
        fig.add_trace(
            go.Scatter(x=avg_dofs, y=median_psd, mode='lines', name="Median PSD", line=dict(color='blue', dash='dot')))

        # Add standard deviation as a filled area
        fig.add_trace(go.Scatter(
            x=np.concatenate([avg_dofs, avg_dofs[::-1]]),
            y=np.concatenate([mean_psd + std_psd, (mean_psd - std_psd)[::-1]]),
            fill='toself',
            fillcolor='rgba(0,100,80,0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo="skip",
            showlegend=False,
            name="Standard Deviation"
        ))

        # Export to CSV if required
        csv_file_path = csv_file_path if csv_file_path else r'C:\Users\prisma\Desktop\test-2\psd_data.csv'
        if export_csv:
            psd_df = pd.DataFrame({
                'DOF': avg_dofs,
                'Mean_PSD': mean_psd,
                'Median_PSD': median_psd,
                'Std_PSD': std_psd
            })
            psd_df.to_csv(csv_file_path, index=False)

        plot_html = to_html(fig, full_html=False)
        print(f'finish, {self.current_start_time}')

        return plot_html, csv_file_path
