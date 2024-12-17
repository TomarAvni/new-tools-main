import sys
sys.path.append(r'C:\Users\prisma\pz\microservices')
import numpy as np
import plotly.graph_objects as go
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
        self.psd_data_list = []  # Store PSD values of each line
        self.dofs_data_list = []  # Store DOFs of each line

    def moving_average(self, data, window_size):
        return np.convolve(data, np.ones(window_size)/window_size, mode='valid')

    def process(self):
        fig = go.Figure()

        while self.current_end_time < self.rec.metadata.end_time:
            print(f"Processing from {self.current_start_time} to {self.current_end_time}")
            mat = self.rec.get_matrix(time_start=self.current_start_time, time_end=self.current_end_time)
            fft_result = np.fft.fft(mat, axis=0)
            freqs = np.fft.fftfreq(mat.shape[0], d=1 / self.fs)
            psd_matrix = np.abs(fft_result) ** 2
            freq_indices = np.where((freqs >= self.low_freq) & (freqs <= self.high_freq))[0]
            gilad_math = psd_matrix[freq_indices, :] / freqs[freq_indices][:, np.newaxis]
            mean_psd_values_per_dof_dB = 10 * np.log10(np.mean(gilad_math, axis=0)) * 2

            smoothed_psd = self.moving_average(mean_psd_values_per_dof_dB, self.smoothing_window)
            dofs = self.rec.metadata.dx * np.arange(len(smoothed_psd))

            # Store data for later use
            self.psd_data_list.append(smoothed_psd)
            self.dofs_data_list.append(dofs)

            # Plot each line
            fig.add_trace(go.Scatter(x=dofs, y=mean_psd_values_per_dof_dB, mode='lines', name=f"PSD {self.current_start_time}"))

            print(f'{self.current_end_time}, done')
            self.current_start_time += self.n * self.td
            self.current_end_time = self.current_start_time + self.td
            print(f'{self.current_end_time}, done')

        # Calculate some thisngs
        psd_data_array = np.array(self.psd_data_list)
        mean_psd = np.mean(psd_data_array, axis=0)
        std_psd = np.std(psd_data_array, axis=0)
        median_psd = np.median(psd_data_array, axis=0)

        # Plot the average line
        avg_dofs = self.dofs_data_list[0]  # Use DOFs from the first trace
        fig.add_trace(go.Scatter(x=avg_dofs, y=mean_psd, mode='lines', name="Average PSD", line=dict(color='black', dash='dash')))

        # Plot the median line
        fig.add_trace(go.Scatter(x=avg_dofs, y=median_psd, mode='lines', name="Median PSD", line=dict(color='blue', dash='dot')))

        # Plot the standard deviation as a shaded area
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

        fig.update_layout(title="Combined PSD Graph", xaxis_title="DOFs", yaxis_title="Mean PSD (dB)")
        fig.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process PSD from recordings.")
    parser.add_argument("--recording_path", type=str, required=True, help="Path to the recording file.")
    parser.add_argument("--td_seconds", type=int, default=1, help="Time delta in seconds for each window.")
    parser.add_argument("--low_freq", type=float, default=1, help="Lower frequency bound for PSD averaging.")
    parser.add_argument("--high_freq", type=float, default=30, help="Upper frequency bound for PSD averaging.")
    parser.add_argument("--n", type=int, default=1800, help="N")
    parser.add_argument("--smoothing_window", type=int, default=10, help="Window size for moving average.")

    args = parser.parse_args()

    analyzer = PSDAnalyzer(
        recording_path=args.recording_path,
        td_seconds=args.td_seconds,
        low_freq=args.low_freq,
        high_freq=args.high_freq,
        n=args.n,
        smoothing_window=args.smoothing_window  # Pass the smoothing window
    )
    analyzer.process()
