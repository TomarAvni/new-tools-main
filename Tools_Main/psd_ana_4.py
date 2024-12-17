import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from pzpy.recording import Recording

sys.path.append(r'C:\Users\prisma\pz\microservices')


class PSDAnalyzer:
    def __init__(self, folder_path, target_t=5, stretcher_length=60, calibration_fiber_length=11500,
                 low_freq=1, high_freq=30, pzt_frequency=100, pulse_length=200, number_of_pulses=18):
        self.folder_path = folder_path
        self.target_t = target_t
        self.stretcher_length = stretcher_length
        self.calibration_fiber_length = calibration_fiber_length
        self.low_freq = low_freq
        self.high_freq = high_freq
        self.pzt_frequency = pzt_frequency
        self.pulse_length = pulse_length
        self.number_of_pulses = number_of_pulses

    def process_recordings(self):
        for filename in os.listdir(self.folder_path):
            print(f"looking in {folder_path}, for {filename}")
            if filename.endswith(".prp2"):  # Assuming recordings have '.dat' extension
                recording_path = os.path.join(self.folder_path, filename)
                print(f"Processing file: {recording_path}")
                signal_rad, SNR_pzt_freq, pzt_psd, dof_m = self.calculate_snr(recording_path)
                print(f"Results for {filename}:")
                print(f"Signal Rad: {signal_rad}")
                print(f"SNR at {self.pzt_frequency} Hz: {SNR_pzt_freq} dB")
                print()
            else:
                print("__cant find recs__")


    def calculate_snr(self, recording_path):
        r = Recording.open_recording(recording_path)
        mat_test = r.get_matrix()
        fiber_length_in_pixels = mat_test.shape[1]

        prr = float(r.metadata.prr)
        dx = float(r.metadata.dx)
        T = 1 / prr
        L = len(mat_test)

        pulse_train_meters = self.pulse_length / 10 * self.number_of_pulses
        crosstalk_distance_meters = pulse_train_meters + (self.stretcher_length / 2)
        crosstalk_distance_pixels = int(np.floor(crosstalk_distance_meters / dx))

        # Time slicing for target duration
        if L / self.target_t == prr:
            print(f"The data is exactly {self.target_t} seconds long")
        elif L / self.target_t < prr:
            print('Data is too short, please add a longer recording')
            raise Exception('Data too short')
        else:
            mat_test = mat_test[:int(self.target_t * prr), :]

        # PSD analysis
        total_pixels = fiber_length_in_pixels - 1
        calibration_fiber_length_pixels = int(np.floor(self.calibration_fiber_length / dx))
        PSD = np.zeros((total_pixels, int(prr / 2)))

        for pixel_index in range(total_pixels):
            long_vector = mat_test[:, pixel_index]  # single column
            multiple_time_sequences = np.reshape(long_vector, (-1, self.target_t), order='F')
            l = len(multiple_time_sequences)
            ft = np.fft.fft(multiple_time_sequences, axis=0)
            abs_fft = np.abs(ft / l)
            positive_abs = abs_fft[:l // 2 + 1, :]
            positive_abs[1:-1, :] = 2 * positive_abs[1:-1, :]
            p = positive_abs * positive_abs
            frequencies = prr * np.arange(0, l // 2 + 1) / l
            average_p = np.mean(p, axis=1)
            PSD[pixel_index, :] = 10 * np.log10(average_p[1:int(prr / 2) + 1])

        pzt_frequency_index = int(PSD.shape[1] * (self.pzt_frequency / (prr / 2))) - 1
        pzt_psd = PSD[:, pzt_frequency_index]
        signal_pzt = np.max(pzt_psd[crosstalk_distance_pixels:calibration_fiber_length_pixels])
        loc_max_PSD = np.where(signal_pzt == pzt_psd)[0][0]
        floor_noise_pzt_freq = float(
            np.mean(pzt_psd[crosstalk_distance_pixels:loc_max_PSD - crosstalk_distance_pixels]))
        SNR_pzt_freq = signal_pzt - floor_noise_pzt_freq
        signal_rad = np.sqrt(10 ** (signal_pzt / 10))

        # Plotting
        plt.figure()
        plt.plot(np.arange(len(pzt_psd)) * dx, pzt_psd, color='black')
        plt.ylim([-110, -10])
        plt.title(f'PSD Analysis at {self.pzt_frequency} Hz')
        plt.xlabel("Distance [m]")
        plt.ylabel(f'Phase noise [dB] at {self.pzt_frequency} Hz')
        plt.legend([f'SNR={round(SNR_pzt_freq, 2)}dB, Signal={round(signal_rad, 6)} rad'])
        plt.grid(True)
        plt.show()

        return round(signal_rad, 6), round(SNR_pzt_freq, 4), pzt_psd, np.arange(len(pzt_psd)) * dx


if __name__ == '__main__':
    print("START")

    # Parameters
    folder_path = r'C:\Users\prisma\Desktop\test-2\1'
    target_t = 5
    stretcher_length = 60
    calibration_fiber_length = 11500
    low_freq = 1
    high_freq = 30
    pzt_frequency = 100
    pulse_length = 200
    number_of_pulses = 18

    # Running the analyzer
    analyzer = PSDAnalyzer(folder_path, target_t, stretcher_length, calibration_fiber_length,
                           low_freq, high_freq, pzt_frequency, pulse_length, number_of_pulses)
    analyzer.process_recordings()

    print("FINISH")
