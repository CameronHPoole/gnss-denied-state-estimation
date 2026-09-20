import pandas as pd
import numpy as np
import os

def generate_logs(num_flights = 1000, max_time = 120):
    print(f"Generating synthetic logs for {num_flights} flights, max time {max_time}")

    # intiate telemetry
    all_telem = []

    for log in range(1, num_flights+1):
        # initiate log parameters
        visual_feature_density = np.random.uniform(0.1, 0.9)    # low is desert / high is unique+known landmarks
        true_vel_m = np.random.uniform(15.0, 45.0)              # generic drone steady state travel speeds

        # TODO improve IMU simulation with xy and z accels, brownian noise, motor harmonics, etc. 
        imu_vibration_g = np.random.uniform(0.15, 0.4)

        # generate time_stamps
        time_stamps = np.arange(0, max_time + 1, 0.1)

        for t in range(0, max_time):
            baseline_noise = np.random.normal(1.0, 0.05)

            # drift conditional on visual feature density
            if visual_feature_density > 0.6:
                NAV_MODE = "VISUAL_NAV"
                drift_error = baseline_noise * t * 0.1
            else:
                NAV_MODE = "IMU_ONLY"
                drift_error = baseline_noise * (t ** 2) * imu_vibration_g * 0.05

            all_telem.append({
                "flight_id": log,
                "time_since_gps_loss_s": t,
                "visual_feature_density": round(visual_feature_density, 2),
                "imu_vibration_g": round(imu_vibration_g, 2),
                "true_velocity_mps": round(true_vel_m, 1),
                "nav_mode_active": NAV_MODE,
                "drift_error_m": round(drift_error, 2)
            })

    # convert to DF
    df = pd.DataFrame(all_telem)
    return df

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(current_dir, "..", "data")

    os.makedirs(target_dir, exist_ok=True)

    output_path = os.path.join(target_dir, "synthetic_flight_logs.csv")
    
    # Generate and save
    df = generate_logs()
    df.to_csv(output_path, index=False)

    print(f"Success! Generated {len(df)} rows of telemetry. Saved to: {output_path}")