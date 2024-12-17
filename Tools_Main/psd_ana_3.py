import sys
sys.path.append(r'C:\Users\prisma\pz\microservices')
import numpy as np
import matplotlib.pyplot as plt
from pzpy.recording import Recording

stretcher_length = 60
calibration_fiber_length = 11500
target_t = 5


def calculate_snr(recording_path, pzt_frequency, pulse_length, number_of_pulses):
    r = Recording.open_recording(recording_path)
    mat_test = r.get_matrix()
    fiber_length_in_pixels = mat_test.shape[1]

    prr = float(r.metadata.prr)
    dx = float(r.metadata.dx)
    GL = float(r.metadata.gauge_length_meters)
    T = 1 / prr
    L = len(mat_test)
    pulse_train_meters = pulse_length / 10 * number_of_pulses
    crosstalk_distance_meters = pulse_train_meters + (stretcher_length / 2)
    crosstalk_distance_pixels = int(np.floor(crosstalk_distance_meters / dx))

    if L / target_t == prr:
        print(f'the data is exactly {target_t} seconds long')
    elif L / target_t < prr:
        print('the data is too short, please add a longer recording')
        raise Exception('the data is too short, please add a longer recording')
    else:
        print(f'the data was longer than {target_t} seconds, and it was cut to {target_t} seconds')
        mat_test = mat_test[:int(target_t * prr), :]

    # FFT for the data
    total_pixels = fiber_length_in_pixels - 1
    calibration_fiber_length_pixels = int(np.floor(calibration_fiber_length / dx))
    PSD = np.zeros((total_pixels, int(prr / 2)))
    flat_PSD = np.zeros((total_pixels, int(prr / 2)))
    mean_power_in_pixel = np.zeros((total_pixels, int(prr / 2)))
    dof_m = np.zeros(total_pixels)

    for pixel_index in range(total_pixels):
        long_vector = mat_test[:, pixel_index]  # single col
        multiple_time_sequences = np.reshape(long_vector, (-1, target_t), order='F')
        l = len(multiple_time_sequences)  # Length of signal
        ft = np.fft.fft(multiple_time_sequences, axis=0)  # fft
        abs_fft = np.abs(ft / l)
        positive_abs = abs_fft[:l // 2 + 1, :]
        positive_abs[1:-1, :] = 2 * positive_abs[1:-1, :]
        p = positive_abs * positive_abs
        frequencies = prr * np.arange(0, l // 2 + 1) / l
        average_p = np.mean(p, axis=1)
        PSD[pixel_index, :] = 10 * np.log10(average_p[1:int(prr / 2) + 1])  # standard PSD
        flat_PSD[pixel_index, :] = 10 * np.log10(average_p[1:int(prr / 2) + 1] / frequencies[1:int(prr / 2) + 1])  # normalized per frequency
        mean_power_in_pixel[pixel_index, :] = average_p[1:int(prr / 2) + 1] / frequencies[1:int(prr / 2) + 1]
        dof_m[pixel_index] = (pixel_index + 1) * dx

    pzt_frequency_index = int(PSD.shape[1] * (pzt_frequency / (prr / 2))) - 1
    pzt_psd = PSD[:, pzt_frequency_index]
    print()

    signal_pzt = np.max(pzt_psd[crosstalk_distance_pixels:calibration_fiber_length_pixels])
    loc_max_PSD = np.where(signal_pzt == pzt_psd)[0][0]
    floor_noise_pzt_freq = float(np.mean(pzt_psd[crosstalk_distance_pixels:loc_max_PSD - crosstalk_distance_pixels]))
    SNR_pzt_freq = signal_pzt - floor_noise_pzt_freq

    signal_rad = np.sqrt(10 ** (signal_pzt / 10))

    signal_rad = round(signal_rad, 6)
    SNR_pzt_freq = round(SNR_pzt_freq, 4)
    print(f"max - {np.max(pzt_psd)}")
    print(f"min - {np.min(pzt_psd)}")

    # Plotting
    plt.figure()
    plt.plot(dof_m, pzt_psd, color='black')
    plt.ylim([-110, -10])
    plt.title(f'TesT')
    plt.xlabel("Distance [m]")
    plt.ylabel(f'Phase noise [dB] at {pzt_frequency}Hz')
    plt.legend([f'SNR={SNR_pzt_freq}dB -PZT {pzt_frequency}Hz {voltage}mVpp, Signal={signal_rad} rad'])
    plt.grid(True)
    plt.show()


    return signal_rad, SNR_pzt_freq, pzt_psd, dof_m

if __name__ == '__main__':
    print("START")

    recording_path = r'C:\Users\prisma\Desktop\test-2\2'
    voltage = 80
    pzt_frequency = 100
    pulse_length = 200
    number_of_pulses = 18
    a, b, c, d= calculate_snr(recording_path,pzt_frequency,pulse_length,number_of_pulses)
    print(f"signal_rad: {a}")
    print(f"SNR_pzt_freq: {b}")
    print(f"pzt_psd: {c}")
    print(f"dof_m: {d}")
    print("FINISH")
