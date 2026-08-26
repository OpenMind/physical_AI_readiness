"""
OpenMind Physical AI Readiness Index (PAIRI) 2026 — dataset construction.

Two composites, both pointing the same way (higher = better):
  PAIRI  — OpenMind Physical AI Readiness Index (capability): can this place BUILD and RUN
           advanced embodied AI at scale? 6 pillars, 0-100.
  OLI    — Operating Latitude Index: how willing are law, labour and the public
           to let it operate? 0-100, higher = more permissive.

Raw indicators are cited in SOURCES.md. Columns ending _s are analyst scores on a
0-100 scale anchored to documented evidence (see METHODOLOGY.md); every such score
carries a rationale in the accompanying notes file. Columns flagged in `flags`
contain at least one analyst-estimated input.
"""
import pathlib
import numpy as np, pandas as pd

# ---------------------------------------------------------------------------
# COLUMN KEY
# iso, name, region
# --- P1 Energy & Grid (hard data: Ember 2025, EIA, Eurostat, GlobalPetrolPrices)
#   gen_twh   total electricity generation, TWh, 2025 (2024 where noted)
#   kwh_cap   electricity demand per capita, kWh
#   cap_g     net installed capacity growth, % YoY 2025
#   price     industrial/business electricity price, USD/kWh
#   grid_s    grid reliability + headroom score 0-100 (analyst, anchored to
#             Enterprise Survey outage data, SAIDI, queue/congestion evidence)
# --- P2 Compute & Semiconductors
#   fab_pct   share of global wafer fab capacity, % (SEMI 2025, regional where national n/a)
#   dc_s      datacenter / AI compute presence score 0-100
#   chip_s    access to advanced AI silicon score 0-100 (export-control adjusted)
#   edge_s    edge/embedded silicon + sensor manufacturing score 0-100
# --- P3 Robotics & Actuation
#   rd        industrial robot density per 10k mfg workers (IFR 2024; est. flagged)
#   inst_k    2024 industrial robot installations, thousands
#   oem_s     domestic robot OEM capability score 0-100
#   comp_s    actuator/reducer/motor/sensor component depth score 0-100
#   hum_s     humanoid programme strength score 0-100
#   mva_bn    manufacturing value added, USD bn (World Bank, latest)
# --- P4 Materials & Supply Chain
#   layers    supply-chain layers held at scale, 0-7 (RE mining, RE separation,
#             metal/alloy, magnet mfg, cell mfg, CAM/AAM, precision mechanics)
#   mag_s     NdFeB magnet / rare earth position score 0-100
#   cell_s    battery cell + component position score 0-100
#   mach_s    machine tool / bearing / precision mechanics score 0-100
# --- P5 Human Capital & Software
#   ai100k    AI authors + inventors per 100k population (AI Index 2026)
#   ai_inv    AI private investment 2025, USD bn
#   dev_m     GitHub developers, millions
#   stem_pct  natural science + engineering share of tertiary graduates, %
#   soft_s    robotics software / foundation-model capability score 0-100
#   integ_s   automation integration & skilled-trades capacity score 0-100
# --- P6 Demand Pull
#   wap_chg   working-age (25-64) population change 2025->2040, %
#   wage      manufacturing wage, USD/month
# --- Deployment friction inputs (0-25 each, HIGHER = MORE FRICTION; these are
#     inverted to latitude components below)
#   f_reg f_lab f_pub f_dep
# ---------------------------------------------------------------------------

C = [
# iso  name            region        gen_twh kwh_cap cap_g price grid_s fab_pct dc_s chip_s edge_s  rd  inst_k oem_s comp_s hum_s mva_bn layers mag_s cell_s mach_s ai100k ai_inv dev_m stem_pct soft_s integ_s wap_chg wage  f_reg f_lab f_pub f_dep
("CHN","China",        "Asia",       10577.7, 7460, 16.7, 0.097, 85, 30.0, 92, 55, 95, 166, 295.0, 92, 98, 100, 4661.4, 7.0, 100, 98, 82,  12.0, 12.41,  9.0, 40.0, 88, 92, -10.9, 1320, 16,  6,  4,  2),
("USA","United States","Americas",    4519.8,13060,  3.0, 0.087, 78,  9.5,100,100, 82, 307,  34.2, 52, 46, 78, 2497.1, 5.0,  38, 44, 46,  64.8,285.88, 28.0, 14.1,100, 60,   4.9, 5250,  9, 17, 22,  4),
("JPN","Japan",        "Asia",        1030.0, 8370,  1.1, 0.204, 97, 13.9, 62, 88, 96, 446,  44.5, 95, 96, 58,  867.1, 5.5,  72, 74, 98,   5.1,  1.11,  3.5, 30.0, 44, 88, -15.2, 2240,  5, 13, 12,  9),
("KOR","South Korea",  "Asia",         624.7,12090,  2.9, 0.118, 97, 16.0, 66, 92, 62,1220,  30.6, 74, 62, 76,  499.2, 4.0,  22, 92, 72,  11.5,  1.78,  2.6, 24.8, 46, 92, -18.2, 4380, 17, 24,  6, 12),
("DEU","Germany",      "Europe",       500.5, 6190,  8.1, 0.189, 88,  3.0, 60, 82, 92, 449,  27.0, 74, 88, 60,  843.7, 4.0,  30, 60, 96,  58.1,  4.09,  3.5, 30.4, 50, 74, -14.5, 4600, 22, 25, 15, 10),
("TWN","Taiwan",       "Asia",         288.9,12500,  1.2, 0.184, 85, 17.2, 52, 90, 74, 302,   8.0, 66, 72, 46,  240.0, 2.0,  12, 30, 78,  30.0,  0.60,  1.2, 32.0, 34, 82, -18.4, 2020,  6, 10, 12, 14),
("SGP","Singapore",    "Asia",          60.2,10300,  9.0, 0.269, 97,  5.3, 72, 90, 52, 818,   1.0, 30, 30, 32,   89.4, 1.0,   4, 12, 30, 109.5,  1.82,  0.6, 24.9, 44, 78,   2.5, 3800,  3,  6,  7,  6),
("CHE","Switzerland",  "Europe",        65.0, 7260,  5.0, 0.286, 95,  1.0, 40, 84, 62, 294,   1.4, 60, 82, 36,  165.7, 2.0,  10, 16, 96, 110.5,  0.90,  0.5, 22.6, 40, 76,  -7.4, 6200,  8, 12, 16,  4),
("NLD","Netherlands",  "Europe",       135.0, 6600,  2.1, 0.077, 72,  1.0, 56, 86, 84, 230,   2.4, 44, 52, 40,  122.3, 2.0,   8, 26, 66,  77.6,  1.30,  1.0, 14.7, 40, 72,  -2.4, 5100, 22, 20, 18, 14),
("SWE","Sweden",       "Europe",       170.3,12830,  1.7, 0.099, 92,  0.4, 44, 84, 34, 377,   1.6, 72, 62, 76,   78.5, 1.5,   8, 34, 78,  80.6,  0.97,  0.6, 22.4, 34, 78,   3.1, 4260, 22, 22, 16, 13),
("DNK","Denmark",      "Europe",        34.5, 6990,  7.3, 0.146, 92,  0.2, 30, 84, 26, 329,   0.9, 66, 40, 34,   75.8, 1.0,   4, 12, 44,  65.3,  0.55,  0.4, 17.4, 32, 76,  -2.9, 5400, 22, 22, 14, 14),
("FRA","France",       "Europe",       570.1, 7150,  4.5, 0.125, 92,  1.0, 50, 84, 74, 190,   4.9, 44, 44, 44,  302.3, 3.5,  24, 40, 62,  27.5,  4.36,  2.8, 21.9, 40, 66,  -1.5, 4300, 22, 22, 17, 15),
("GBR","United Kingdom","Europe",      292.3, 4620,  3.9, 0.320, 88,  0.5, 58, 88, 56, 112,   2.5, 30, 40, 52,  294.3, 1.5,   6, 24, 44,  49.6,  5.90,  4.0, 22.7, 52, 56,   3.6, 4690,  7, 13, 20, 11),
("CAN","Canada",       "Americas",     652.4,16090,  0.7, 0.107, 88,  0.3, 44, 90, 26, 241,   3.8, 32, 26, 30,  187.2, 1.5,  10, 30, 34,  76.2,  4.28,  2.6, 19.1, 44, 62,   5.7, 4050,  8, 15, 22, 16),
("ITA","Italy",        "Europe",       264.9, 5270,  6.5, 0.186, 86,  0.6, 34, 84, 72, 240,   8.8, 56, 66, 34,  352.9, 2.0,   8, 26, 88,  22.4,  0.80,  1.4, 23.0, 26, 70, -17.7, 3300, 24, 20, 19, 20),
("ISR","Israel",       "MENA",          82.1, 7950,  7.3, 0.112, 88,  0.6, 34, 88, 66,  50,   0.4, 32, 30, 40,   60.1, 1.0,   4,  8, 30,  52.0,  3.89,  0.5, 45.7, 56, 62,  25.1, 6040,  5, 14, 10, 15),
("ESP","Spain",        "Europe",       288.0, 5750,  7.1, 0.138, 84,  0.4, 34, 84, 46, 180,   5.1, 34, 34, 34,  187.1, 1.5,   6, 30, 46,  17.0,  0.70,  1.8, 18.4, 24, 62, -13.2, 3160, 22, 20, 17, 20),
("AUT","Austria",      "Europe",        73.3, 8490,  6.3, 0.185, 92,  0.5, 26, 84, 58, 220,   1.2, 46, 62, 26,   80.9, 1.0,   4, 14, 74,  50.0,  0.30,  0.4, 26.7, 22, 74, -12.6, 4400, 22, 23, 15, 20),
("BEL","Belgium",      "Europe",        66.9, 6830, -1.8, 0.153, 90,  0.3, 30, 84, 42, 230,   1.1, 30, 34, 24,   76.8, 1.0,   4, 12, 40,  50.0,  1.20,  0.5, 14.9, 24, 68,  -3.0, 4700, 22, 23, 20, 16),
("FIN","Finland",      "Europe",        82.3,15620,  4.5, 0.081, 92,  0.2, 34, 84, 26, 150,   0.5, 34, 30, 40,   42.5, 1.0,   6, 16, 46,  77.6,  0.40,  0.3, 21.1, 30, 70,  -1.6, 4200, 22, 21, 14, 11),
("NOR","Norway",       "Europe",       160.8,24500,  0.5, 0.075, 92,  0.1, 42, 84, 20,  90,   0.3, 34, 20, 26,   29.8, 1.0,   4, 14, 32,  60.0,  0.40,  0.3, 18.4, 46, 66,  -0.1, 6290, 18, 21, 14, 13),
("POL","Poland",       "Europe",       172.6, 4550,  5.7, 0.132, 86,  0.3, 30, 84, 26, 110,   2.6, 20, 22, 16,  147.5, 1.0,   2, 46, 38,  20.0,  0.30,  1.2, 17.9, 18, 58,  -9.8, 2490, 22, 12, 18, 18),
("CZE","Czechia",      "Europe",        75.5, 6420,  0.4, 0.170, 88,  0.2, 24, 84, 30, 200,   2.6, 20, 26, 18,   69.0, 1.0,   2, 24, 44,  20.0,  0.15,  0.5, 21.2, 16, 62,  -9.8, 2320, 22, 11, 16, 18),
("HUN","Hungary",      "Europe",        40.2, 5110,  4.8, 0.196, 86,  0.1, 20, 84, 22,  150,  1.4, 14, 18, 14,   35.2, 1.0,   2, 52, 30,  18.0,  0.10,  0.3, 17.9, 14, 58, -10.9, 2200, 22, 11, 16, 18),
("IND","India",        "Asia",        2081.6, 1420,  9.9, 0.124, 55,  0.5, 42, 78, 26,  10,   9.1, 16, 20, 26,  493.0, 1.5,  14, 22, 30,   3.5,  1.50, 21.9, 27.1, 34, 40,  19.5,  330,  5, 12,  8, 20),
("VNM","Vietnam",      "Asia",         310.0, 3090,  4.6, 0.078, 70,  1.0, 22, 76, 18,  40,   1.0, 10, 14,  8,  116.4, 2.5,  22, 12, 18,   2.0,  0.10,  0.6, 20.6, 10, 40,   6.1,  420, 18,  8,  8, 18),
("MYS","Malaysia",     "Asia",         201.1, 5560,  2.9, 0.129, 82,  1.5, 40, 82, 34,  80,   0.6, 12, 14, 10,   95.0, 1.5,  16, 12, 22,   6.0,  0.20,  0.5, 32.3, 12, 46,  22.8,  840,  4,  7,  6, 16),
("THA","Thailand",     "Asia",         188.2, 3140,  7.0, 0.128, 78,  0.8, 30, 80, 20,  90,   2.5, 10, 16, 10,  128.1, 1.5,   8, 12, 20,   3.0,  0.10,  0.5, 23.3,  8, 44, -10.2,  700,  4,  7,  6, 16),
("IDN","Indonesia",    "Asia",         371.5, 1310,  8.2, 0.070, 65,  0.2, 26, 78, 12,   15,  0.4,  6,  8,  6,  265.1, 1.5,  10, 20, 12,   1.5,  0.10,  4.4, 11.2,  8, 32,  11.1,  200,  4,  7,  6, 16),
("PHL","Philippines",  "Asia",         123.1, 1050,  7.4, 0.154, 55,  0.4, 22, 78, 14,   30,  0.3,  6,  8,  4,   72.4, 0.5,   2,  6, 10,   1.5,  0.05,  1.7, 16.8,  8, 30,  26.7,  420,  4,  9,  8, 17),
("AUS","Australia",    "Oceania",      286.7,10630,  3.8, 0.240, 88,  0.1, 40, 88, 12,   90,  1.0, 14, 12, 22,   94.5, 2.0,  26, 12, 20,  53.4,  3.58,  1.2, 12.8, 30, 52,   8.3, 5020,  5, 16, 21, 18),
("NZL","New Zealand",  "Oceania",       43.3, 8250,  2.5, 0.160, 88,  0.0, 20, 88,  8,   40,  0.2, 12,  8, 12,   22.2, 0.5,   0,  4, 16,  45.0,  0.10,  0.2, 14.8, 22, 48,   3.3, 4200,  5, 13, 16, 17),
("MEX","Mexico",       "Americas",     357.0, 2700,  2.5, 0.212, 60,  0.1, 26, 82, 18,   62,  5.6,  8, 14, 10,  367.6, 0.5,   2, 10, 22,   6.0,  0.20,  1.9, 19.9,  8, 44,  15.1,  865,  5, 11, 16, 18),
("BRA","Brazil",       "Americas",     750.5, 3580,  6.5, 0.131, 65,  0.1, 30, 82, 12,   30,  1.9,  8, 10, 12,  264.7, 1.0,   8,  8, 18,   4.7,  0.40,  6.9, 15.0, 14, 40,   2.1,  650, 12, 14, 21, 18),
("TUR","Turkey",       "Europe",       353.9, 4010,  6.2, 0.141, 70,  0.1, 22, 80, 16,   60,  1.4, 10, 14, 10,  228.9, 0.5,   2, 12, 24,   5.0,  0.10,  1.7, 17.7,  8, 44,   6.4,  800,  5,  9, 13, 17),
("SAU","Saudi Arabia", "MENA",         454.6,13390,  3.7, 0.069, 84,  0.0, 54, 84,  6,   20,  0.3,  4,  4, 18,  194.9, 0.5,   2,  4, 10,   9.9,  2.03,  0.3, 15.2, 16, 30,  24.8, 1800,  3,  4,  5,  5),
("ARE","UAE",          "MENA",         177.3,16050,  3.8, 0.110, 86,  0.0, 58, 84,  6,   30,  0.2,  4,  4, 16,   51.8, 0.5,   2,  4,  8,  28.4,  1.00,  0.3, 21.3, 20, 32,  19.4, 2200,  3,  4,  4,  2),
("QAT","Qatar",        "MENA",          56.2,18030,  6.5, 0.036, 84,  0.0, 26, 84,  4,   15,  0.1,  2,  2,  6,   25.0, 0.0,   0,  2,  6,  20.0,  0.20,  0.1, 20.8, 10, 26,  14.0, 2400,  3,  4,  6, 10),
("IRL","Ireland",      "Europe",        31.0, 6990,  9.8, 0.257, 70,  0.2, 46, 84, 30,   60,  0.4, 12, 12, 14,  180.1, 0.5,   2,  6, 24,  55.0,  0.60,  0.3, 18.3, 30, 54,   7.8, 6350, 22, 16, 19, 18),
("PRT","Portugal",     "Europe",        51.1, 5800,  4.6, 0.125, 86,  0.1, 26, 84, 16,   90,  0.6, 12, 12, 12,   36.8, 1.0,   2,  8, 26,  20.0,  0.10,  0.4, 27.2, 12, 50, -13.2, 1900, 22, 17, 15, 19),
("GRC","Greece",       "Europe",        57.9, 5570, 11.6, 0.192, 84,  0.0, 20, 84,  8,   30,  0.2,  6,  6,  6,   23.2, 0.0,   0,  2, 14,  18.0,  0.05,  0.3, 25.2,  8, 40, -13.2, 1500, 22, 17, 20, 20),
("ROU","Romania",      "Europe",        49.8, 2840,  9.3, 0.172, 78,  0.1, 18, 84, 14,   50,  0.5,  6,  8,  6,   50.5, 0.0,   0,  6, 20,  16.0,  0.05,  0.4, 23.8, 10, 44, -14.3, 2080, 22, 11, 16, 18),
("EST","Estonia",      "Europe",         6.2, 6620,  0.3, 0.139, 88,  0.0, 16, 84,  6,   60,  0.1,  6,  6,  6,    5.0, 2.5,  40,  4, 10,  40.0,  0.05,  0.1, 21.1, 12, 46, -10.2, 2270, 22, 11, 16, 18),
("SVK","Slovakia",     "Europe",        29.1, 4880,  4.1, 0.187, 86,  0.0, 14, 84, 10,  190,  0.8, 10, 12, 10,   23.0, 0.5,   0, 14, 22,  16.0,  0.05,  0.2, 20.0,  8, 56,  -9.8, 2120, 22, 11, 16, 18),
("SVN","Slovenia",     "Europe",        14.9, 6800,  2.4, 0.155, 88,  0.0, 12, 84,  8,  315,  0.4, 14, 12,  8,   14.1, 0.0,   0,  4, 20,  25.0,  0.05,  0.1, 21.0,  8, 58,  -9.8, 2990, 22, 11, 16, 18),
("RUS","Russia",       "Europe",      1192.8, 8170,  1.3, 0.097, 70,  0.2, 14,  6, 10,   15,  0.5, 10,  8,  6,  288.1, 2.0,  16, 10, 34,  10.0,  0.10,  1.5, 25.9,  8, 40,  -6.3, 1340, 20, 12, 14, 18),
("UKR","Ukraine",      "Europe",       111.5, 2720,  0.0, 0.149, 15,  0.0, 10, 70,  4,   10,  0.1,  4,  6,  8,   16.0, 0.0,   0,  2, 14,  12.0,  0.05,  0.3, 19.6, 12, 34,  -9.0,  600,  4, 10, 14, 20),
("ZAF","South Africa", "Africa",       242.8, 3660,  5.9, 0.100, 25,  0.0, 20, 80,  6,   35,  0.3,  4,  6,  6,   51.3, 0.5,   4,  4, 12,   6.0,  0.10,  0.7, 15.3,  8, 32,  16.2, 1400,  4, 10, 14, 19),
("EGY","Egypt",        "Africa",       245.7, 2060,  2.5, 0.037, 60,  0.0, 14, 78,  4,    5,  0.1,  2,  2,  2,   54.1, 0.0,   0,  2,  6,   2.0,  0.05,  1.0,  9.8,  4, 22,  33.1,  350,  4,  8, 12, 19),
("NGA","Nigeria",      "Africa",        41.5,  170,  0.3, 0.050,  5,  0.0,  8, 78,  2,    2,  0.0,  2,  2,  2,   21.8, 0.0,   0,  0,  4,   1.0,  0.05,  1.1,  8.0,  4, 14,  54.3,  250,  3,  8, 14, 20),
("KEN","Kenya",        "Africa",        14.0,  270,  0.0, 0.175, 25,  0.0,  8, 78,  2,    2,  0.0,  2,  2,  2,    8.0, 0.0,   0,  0,  4,   1.0,  0.05,  0.4, 11.2,  6, 14,  49.7,  260,  3,  8, 13, 20),
("MAR","Morocco",      "Africa",        44.2, 1250,  1.9, 0.109, 65,  0.0, 12, 78,  6,   15,  0.1,  2,  4,  4,   26.0, 0.5,   2, 10, 10,   2.0,  0.05,  0.6, 15.1,  4, 26,  13.9,  450,  3,  8, 13, 19),
("ARG","Argentina",    "Americas",     153.1, 3540,  2.6, 0.094, 60,  0.0, 14, 80,  4,   20,  0.1,  4,  6,  6,   96.9, 0.5,   2,  4, 12,   6.0,  0.10,  1.1, 10.3,  8, 34,  13.5,  700,  5, 11, 16, 18),
("CHL","Chile",        "Americas",      88.5, 4460,  5.8, 0.161, 70,  0.0, 18, 82,  4,   15,  0.1,  2,  4,  4,   30.0, 1.0,   2,  6,  8,   8.0,  0.10,  0.3, 18.0,  8, 32,   2.5, 1100,  5, 11, 16, 18),
("COL","Colombia",     "Americas",      90.4, 1720,  1.1, 0.202, 60,  0.0, 12, 80,  2,   10,  0.1,  2,  2,  4,   40.0, 0.0,   0,  2,  6,   4.0,  0.05,  1.0, 18.3,  6, 26,  10.7,  500,  5, 11, 16, 18),
("KAZ","Kazakhstan",   "Asia",         123.7, 6050,  5.2, 0.074, 60,  0.0, 10, 78,  2,    5,  0.0,  2,  2,  2,   36.1, 0.5,   2,  2,  8,   3.0,  0.05,  0.2, 21.8,  4, 24,  12.8, 1100, 14,  8, 12, 18),
("PAK","Pakistan",     "Asia",         177.1,  700,  1.4, 0.155, 10,  0.0,  8, 76,  2,    2,  0.0,  2,  2,  2,   48.9, 0.0,   0,  0,  4,   1.0,  0.05,  0.4, 10.0,  4, 16,  44.3,  200,  3,  8, 12, 20),
("BGD","Bangladesh",   "Asia",         103.4,  670,  6.4, 0.100,  8,  0.0,  8, 76,  2,    2,  0.0,  2,  2,  2,   98.5, 0.0,   0,  0,  4,   1.0,  0.05,  0.3,  9.3,  4, 16,  27.7,  180,  4,  8, 12, 20),
]

COLS = ["iso","name","region","gen_twh","kwh_cap","cap_g","price","grid_s","fab_pct","dc_s",
        "chip_s","edge_s","rd","inst_k","oem_s","comp_s","hum_s","mva_bn","layers","mag_s",
        "cell_s","mach_s","ai100k","ai_inv","dev_m","stem_pct","soft_s","integ_s","wap_chg",
        "wage","f_reg","f_lab","f_pub","f_dep"]
df = pd.DataFrame(C, columns=COLS).set_index("iso")

# --- normalisation helpers -------------------------------------------------
def mm(s, lo=None, hi=None, invert=False):
    """min-max to 0-100 with optional winsorising bounds."""
    x = s.astype(float).copy()
    lo = x.min() if lo is None else lo
    hi = x.max() if hi is None else hi
    x = x.clip(lo, hi)
    z = (x - lo) / (hi - lo) * 100
    return 100 - z if invert else z

def logscale(s, floor=0.01):
    return np.log10(s.astype(float).clip(lower=floor))

W = {"P1_energy":0.15,"P2_compute":0.15,"P3_robotics":0.25,
     "P4_materials":0.15,"P5_human":0.20,"P6_demand":0.10}


def compute(df):
    """Raw indicator table -> pillar scores, PAIRI, OLI, EFFECTIVE.

    Kept as a function so bootstrap.py can re-run it on perturbed inputs."""
    df = df.copy()
# ---------------------------------------------------------------------------
# PILLAR 1 — ENERGY & GRID  (weight 0.15)
#   scale of the electricity system (log), intensity per capita, build rate,
#   industrial price, reliability
# ---------------------------------------------------------------------------
    p1 = (0.30*mm(logscale(df.gen_twh))
        + 0.20*mm(df.kwh_cap, 200, 20000)
        + 0.20*mm(df.cap_g, 0, 15)
        + 0.20*mm(df.price, 0.05, 0.30, invert=True)
        + 0.10*df.grid_s)
    df["P1_energy"] = p1

    # ---------------------------------------------------------------------------
    # PILLAR 2 — COMPUTE & SEMICONDUCTORS  (weight 0.15)
    # ---------------------------------------------------------------------------
    df["P2_compute"] = (0.25*mm(logscale(df.fab_pct + 0.02))
                      + 0.30*df.dc_s
                      + 0.20*df.chip_s
                      + 0.25*df.edge_s)

    # ---------------------------------------------------------------------------
    # PILLAR 3 — ROBOTICS & ACTUATION  (weight 0.25) — the heaviest pillar
    # ---------------------------------------------------------------------------
    df["P3_robotics"] = (0.18*mm(df.rd, 0, 900)
                       + 0.14*mm(logscale(df.inst_k + 0.05))
                       + 0.20*df.oem_s
                       + 0.24*df.comp_s
                       + 0.10*df.hum_s
                       + 0.14*mm(logscale(df.mva_bn)))

    # ---------------------------------------------------------------------------
    # PILLAR 4 — MATERIALS & SUPPLY CHAIN  (weight 0.15)
    # ---------------------------------------------------------------------------
    df["P4_materials"] = (0.22*mm(df.layers, 0, 7)
                        + 0.34*df.mag_s
                        + 0.20*df.cell_s
                        + 0.24*df.mach_s)

    # ---------------------------------------------------------------------------
    # PILLAR 5 — HUMAN CAPITAL & SOFTWARE  (weight 0.20)
    # ---------------------------------------------------------------------------
    df["P5_human"] = (0.14*mm(df.ai100k, 0, 110)
                    + 0.16*mm(logscale(df.ai_inv + 0.02))
                    + 0.14*mm(logscale(df.dev_m + 0.02))
                    + 0.08*mm(df.stem_pct, 5, 40)
                    + 0.24*df.soft_s
                    + 0.24*df.integ_s)

    # ---------------------------------------------------------------------------
    # PILLAR 6 — DEMAND PULL  (weight 0.10)
    #   shrinking workforce + high manufacturing wage + large industrial base
    #   = strong economic pull for embodied automation
    # ---------------------------------------------------------------------------
    df["P6_demand"] = (0.45*mm(df.wap_chg, -20, 30, invert=True)
                     + 0.35*mm(logscale(df.wage), np.log10(180), np.log10(6500))
                     + 0.20*mm(logscale(df.mva_bn)))

    df["PAIRI"] = sum(df[k]*w for k, w in W.items())

    # ---------------------------------------------------------------------------
    # DEPLOYMENT EAGERNESS INDEX (0-100, higher = more permissive to let robots work)
    # Each component is the inverse of its friction input, so 25 = maximally
    # permissive/welcoming on that dimension and 0 = maximally constrained.
    # ---------------------------------------------------------------------------
    df["e_law"]    = 25 - df.f_reg   # AI, machinery and liability law
    df["e_labour"] = 25 - df.f_lab   # unions, works councils, employment protection
    df["e_public"] = 25 - df.f_pub   # public sentiment and institutional trust
    df["e_auto"]   = 25 - df.f_dep   # demonstrated autonomy permissiveness
    df["OLI"] = df.e_law + df.e_labour + df.e_public + df.e_auto

    # Effective near-term deployment potential. Reluctance delays and raises the cost
    # of deployment rather than preventing it, so a zero-latitude country still
    # retains 45% of its capability score.
    df["EFFECTIVE"] = df.PAIRI * (0.45 + 0.55*df.OLI/100)

    return df


df_raw = df.copy()
df = compute(df)
df["rank"] = df.PAIRI.rank(ascending=False).astype(int)
df = df.sort_values("PAIRI", ascending=False)

out = df.reset_index()[["iso","name","region","PAIRI","rank","P1_energy","P2_compute",
    "P3_robotics","P4_materials","P5_human","P6_demand","OLI","e_law","e_labour",
    "e_public","e_auto","EFFECTIVE","gen_twh","kwh_cap","cap_g","price","rd","inst_k",
    "mva_bn","layers","ai100k","ai_inv","dev_m","wap_chg","wage"]].round(2)
pathlib.Path("out").mkdir(exist_ok=True)
out.to_csv("out/pairi_2026.csv", index=False)

pd.set_option("display.width", 250, "display.max_columns", 40)
print(out.head(30).to_string(index=False))
print("\n--- Latitude-adjusted top 20 ---")
print(df.sort_values("EFFECTIVE", ascending=False)[["name","PAIRI","OLI","EFFECTIVE"]]
        .head(20).round(1).to_string(index=False))
print(f"\nCountries: {len(df)}   PAIRI range: {df.PAIRI.min():.1f} - {df.PAIRI.max():.1f}")

# ---------------------------------------------------------------------------
# METRO CLUSTER SCORES
# Same six pillars, same weights, scored at cluster rather than national level.
# Analyst scores anchored to the cluster research documented in the report.
# `q36` is the separate qualitative ranking on capacity to design, build and
# deploy at volume within 36 months, retained because it answers a different
# question from the capability index.
# ---------------------------------------------------------------------------
CL = [
# key                     label                          country  lat     lon    C1  C2  C3  C4  C5  C6   OLI q36
("Shenzhen",  "Shenzhen-Dongguan-Guangzhou",  "China",  22.54, 114.06, 85, 78, 98, 92, 82, 74, 74,  1),
("Shanghai",  "Shanghai-Suzhou-Hangzhou",     "China",  31.23, 121.47, 84, 80, 93, 90, 84, 76, 72,  2),
("Tokyo",     "Tokyo-Kanagawa",               "Japan",  35.68, 139.69, 70, 84, 88, 84, 70, 80, 61,  6),
("Seoul",     "Seoul-Gyeonggi + Ulsan",       "Korea",  37.57, 126.98, 78, 80, 88, 58, 72, 92, 39,  4),
("Beijing",   "Beijing (Haidian + Yizhuang)", "China",  39.90, 116.40, 80, 88, 62, 52, 88, 74, 72, 10),
("Hefei",     "Hefei-Wuhu",                   "China",  31.82, 117.23, 82, 62, 80, 74, 58, 72, 74, 13),
("Nagoya",    "Nagoya-Toyota (Chubu)",        "Japan",  35.18, 136.91, 68, 60, 86, 72, 58, 80, 61, 16),
("Taichung",  "Hsinchu-Taichung-Taipei",      "Taiwan", 24.15, 120.67, 66, 92, 76, 44, 66, 80, 58,  8),
("BayArea",   "Bay Area (SF / Silicon Valley)","USA",   37.44,-122.14, 62,100, 58, 32,100, 66, 52,  3),
("Stuttgart", "Stuttgart-Karlsruhe",          "Germany",48.78,   9.18, 58, 66, 80, 56, 72, 86, 28,  7),
("Munich",    "Munich-Augsburg",              "Germany",48.14,  11.58, 58, 66, 74, 48, 76, 84, 28, 11),
("Hefei2",    "",                             "",        0.0,    0.0,  0,  0,  0,  0,  0,  0,  0,  0),
("Boston",    "Boston-Cambridge",             "USA",    42.36, -71.06, 60, 76, 70, 34, 88, 64, 52,  5),
("Zurich",    "Zurich-Basel",                 "Switz.", 47.38,   8.54, 66, 58, 68, 32, 86, 78, 60, 15),
("Eindhoven", "Eindhoven-Brainport",          "Neth.",  51.44,   5.48, 54, 80, 64, 30, 76, 72, 26, 20),
("Singapore", "Singapore",                    "S'pore",  1.35, 103.82, 62, 72, 70, 16, 74, 64, 78, 21),
("Gothenburg","Vasteras-Gothenburg",          "Sweden", 57.71,  11.97, 70, 46, 74, 32, 64, 64, 27, 19),
("Austin",    "Austin",                       "USA",    30.27, -97.74, 72, 74, 50, 26, 72, 62, 60, 12),
("Bologna",   "Milan-Bologna-Modena",         "Italy",  44.49,  11.34, 56, 44, 72, 34, 54, 84, 17, 18),
("Pittsburgh","Pittsburgh",                   "USA",    40.44, -79.99, 62, 60, 52, 26, 80, 60, 52,  9),
("Odense",    "Odense / Funen",               "Denmark",55.40,  10.39, 64, 40, 72, 22, 62, 70, 28, 14),
("Detroit",   "Detroit-Ann Arbor",            "USA",    42.33, -83.05, 64, 52, 60, 28, 62, 70, 45, 17),
("Bengaluru", "Bengaluru",                    "India",  12.97,  77.59, 50, 52, 26, 18, 66, 30, 55, 22),
]
cl = pd.DataFrame([c for c in CL if c[1]], columns=["key","label","country","lat","lon",
     "C1_energy","C2_compute","C3_robotics","C4_materials","C5_human","C6_demand",
     "OLI","q36"]).set_index("key")
cl["PAIRI"] = (0.15*cl.C1_energy + 0.15*cl.C2_compute + 0.25*cl.C3_robotics
           + 0.15*cl.C4_materials + 0.20*cl.C5_human + 0.10*cl.C6_demand)
cl["EFFECTIVE"] = cl.PAIRI * (0.45 + 0.55*cl.OLI/100)
cl = cl.sort_values("PAIRI", ascending=False)
cl["rank"] = range(1, len(cl) + 1)
cl.reset_index().round(2).to_csv("out/pairi_clusters_2026.csv", index=False)
print("\n--- Metro clusters ---")
print(cl.reset_index()[["rank","label","country","PAIRI","OLI","EFFECTIVE","q36"]]
        .round(1).to_string(index=False))
