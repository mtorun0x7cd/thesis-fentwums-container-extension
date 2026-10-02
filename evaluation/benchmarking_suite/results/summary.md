# Evaluation summary

Mean execution time (95% CI) per workload and backend, by platform. Overhead x is the
container-vs-native ratio (where a native baseline was measured); Ext. overhead x is the
strategy-vs-CLI ratio — the cost the extension adds beyond raw containerization.

## linux-amd64 — Intel(R) Core(TM) Ultra 9 285H (61.0 GB, 16 cores, Docker 29.1.3)

| Workload | Backend | n | Mean (s) | 95% CI (s) | CV% | Overhead x | Ext. overhead x |
|---|---|---|---|---|---|---|---|
| lifecycle_floor | native | 60 | 0.0012 | [0.0010, 0.0013] | 37.4 |  |  |
| lifecycle_floor | cli | 30 | 0.3283 | [0.3164, 0.3403] | 9.8 | 284.89x |  |
| lifecycle_floor | strategy | 30 | 0.5069 | [0.4983, 0.5156] | 4.6 | 439.86x | 1.54x |
| pack_ecp5_ecppack | native | 30 | 0.5125 | [0.5077, 0.5172] | 2.5 |  |  |
| pack_ecp5_ecppack | cli | 30 | 0.7710 | [0.7635, 0.7785] | 2.6 | 1.50x |  |
| pack_ecp5_ecppack | strategy | 30 | 1.0049 | [0.9955, 1.0143] | 2.5 | 1.96x | 1.30x |
| pack_ice40_icepack | native | 30 | 0.0159 | [0.0158, 0.0160] | 1.1 |  |  |
| pack_ice40_icepack | cli | 30 | 0.3148 | [0.3147, 0.3149] | 0.1 | 19.80x |  |
| pack_ice40_icepack | strategy | 30 | 0.5236 | [0.5150, 0.5322] | 4.4 | 32.94x | 1.66x |
| pnr_ecp5_nextpnr | native | 30 | 0.3686 | [0.3639, 0.3734] | 3.5 |  |  |
| pnr_ecp5_nextpnr | cli | 30 | 0.6656 | [0.6655, 0.6657] | 0.0 | 1.81x |  |
| pnr_ecp5_nextpnr | strategy | 30 | 0.8711 | [0.8621, 0.8801] | 2.8 | 2.36x | 1.31x |
| pnr_ice40_nextpnr | native | 30 | 0.0643 | [0.0642, 0.0644] | 0.3 |  |  |
| pnr_ice40_nextpnr | cli | 30 | 0.3481 | [0.3391, 0.3571] | 6.9 | 5.41x |  |
| pnr_ice40_nextpnr | strategy | 30 | 0.5605 | [0.5529, 0.5681] | 3.6 | 8.72x | 1.61x |
| sim_iverilog | native | 30 | 0.0319 | [0.0319, 0.0320] | 0.3 |  |  |
| sim_iverilog | cli | 30 | 0.3182 | [0.3135, 0.3230] | 4.0 | 9.97x |  |
| sim_iverilog | strategy | 30 | 0.5203 | [0.5146, 0.5261] | 3.0 | 16.30x | 1.64x |
| synth_ecp5_yosys | native | 30 | 0.2649 | [0.2648, 0.2649] | 0.1 |  |  |
| synth_ecp5_yosys | cli | 30 | 0.5822 | [0.5708, 0.5935] | 5.2 | 2.20x |  |
| synth_ecp5_yosys | strategy | 30 | 0.7656 | [0.7557, 0.7754] | 3.4 | 2.89x | 1.31x |
| synth_ice40_yosys | native | 30 | 0.3570 | [0.3499, 0.3640] | 5.3 |  |  |
| synth_ice40_yosys | cli | 30 | 0.6154 | [0.6152, 0.6155] | 0.1 | 1.72x |  |
| synth_ice40_yosys | strategy | 30 | 0.8244 | [0.8173, 0.8314] | 2.3 | 2.31x | 1.34x |

## macos-arm64 — Apple M4 Max (128.0 GB, 16 cores, Docker 29.4.0)

| Workload | Backend | n | Mean (s) | 95% CI (s) | CV% | Overhead x | Ext. overhead x |
|---|---|---|---|---|---|---|---|
| lifecycle_floor | cli | 30 | 0.2504 | [0.2391, 0.2617] | 12.1 |  |  |
| lifecycle_floor | strategy | 48 | 0.4520 | [0.4323, 0.4718] | 15.0 |  | 1.81x |
| pack_ecp5_ecppack | cli | 30 | 0.9976 | [0.9895, 1.0058] | 2.2 |  |  |
| pack_ecp5_ecppack | strategy | 30 | 1.1785 | [1.1685, 1.1885] | 2.3 |  | 1.18x |
| pack_ice40_icepack | cli | 30 | 0.3490 | [0.3406, 0.3575] | 6.5 |  |  |
| pack_ice40_icepack | strategy | 30 | 0.5634 | [0.5553, 0.5715] | 3.9 |  | 1.61x |
| pnr_ecp5_nextpnr | cli | 30 | 1.0036 | [0.9925, 1.0146] | 3.0 |  |  |
| pnr_ecp5_nextpnr | strategy | 30 | 1.1866 | [1.1779, 1.1953] | 2.0 |  | 1.18x |
| pnr_ice40_nextpnr | cli | 30 | 0.6309 | [0.6208, 0.6410] | 4.3 |  |  |
| pnr_ice40_nextpnr | strategy | 30 | 0.8207 | [0.8129, 0.8286] | 2.6 |  | 1.30x |
| sim_iverilog | cli | 30 | 0.5283 | [0.5189, 0.5378] | 4.8 |  |  |
| sim_iverilog | strategy | 30 | 0.7130 | [0.7087, 0.7172] | 1.6 |  | 1.35x |
| synth_ecp5_yosys | cli | 30 | 1.1647 | [1.1537, 1.1757] | 2.5 |  |  |
| synth_ecp5_yosys | strategy | 30 | 1.3111 | [1.2955, 1.3268] | 3.2 |  | 1.13x |
| synth_ice40_yosys | cli | 30 | 1.3456 | [1.3327, 1.3584] | 2.5 |  |  |
| synth_ice40_yosys | strategy | 30 | 1.5042 | [1.4951, 1.5134] | 1.6 |  | 1.12x |

## windows-amd64 — Intel64 Family 6 Model 170 Stepping 4, GenuineIntel (31.46 GB, 22 cores, Docker 29.6.1)

| Workload | Backend | n | Mean (s) | 95% CI (s) | CV% | Overhead x | Ext. overhead x |
|---|---|---|---|---|---|---|---|
| lifecycle_floor | cli | 30 | 0.4227 | [0.4161, 0.4293] | 4.2 |  |  |
| lifecycle_floor | strategy | 30 | 0.6775 | [0.6658, 0.6892] | 4.6 |  | 1.60x |
| pack_ecp5_ecppack | cli | 30 | 1.1550 | [1.1444, 1.1655] | 2.5 |  |  |
| pack_ecp5_ecppack | strategy | 30 | 1.3314 | [1.3192, 1.3435] | 2.4 |  | 1.15x |
| pack_ice40_icepack | cli | 30 | 0.4472 | [0.4419, 0.4525] | 3.2 |  |  |
| pack_ice40_icepack | strategy | 30 | 0.6975 | [0.6924, 0.7026] | 2.0 |  | 1.56x |
| pnr_ecp5_nextpnr | cli | 30 | 1.1533 | [1.1421, 1.1645] | 2.6 |  |  |
| pnr_ecp5_nextpnr | strategy | 30 | 1.4034 | [1.3729, 1.4338] | 5.8 |  | 1.22x |
| pnr_ice40_nextpnr | cli | 30 | 1.5436 | [1.5341, 1.5531] | 1.6 |  |  |
| pnr_ice40_nextpnr | strategy | 60 | 2.1905 | [2.0874, 2.2935] | 18.1 |  | 1.42x |
| sim_iverilog | cli | 30 | 0.4595 | [0.4540, 0.4650] | 3.2 |  |  |
| sim_iverilog | strategy | 30 | 0.6815 | [0.6755, 0.6875] | 2.4 |  | 1.48x |
| synth_ecp5_yosys | cli | 30 | 0.8801 | [0.8724, 0.8878] | 2.3 |  |  |
| synth_ecp5_yosys | strategy | 30 | 1.1596 | [1.1307, 1.1884] | 6.7 |  | 1.32x |
| synth_ice40_yosys | cli | 30 | 0.9849 | [0.9742, 0.9956] | 2.9 |  |  |
| synth_ice40_yosys | strategy | 30 | 1.1797 | [1.1386, 1.2207] | 9.3 |  | 1.20x |

