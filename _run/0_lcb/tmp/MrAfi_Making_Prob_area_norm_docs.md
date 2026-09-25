# Documentation: MrAfi_Making_Prob_area_norm.py

## [English]

### Overview
This script calculates and visualizes the Boltzmann-weighted probability density distributions of atomic structures across various temperatures ($T$) using structural trajectory data and Gaussian Kernel Density Estimation (KDE). Crucially, the probability density curves are normalized so that the total area under each curve equals 1 (Area Normalization via the trapezoidal rule).

### Key Features & Workflow
1. **Directory Setup**: Automatically creates required analysis directories (`0_analy/0_xsf_traj`, `0_analy/1_xsf`, etc.).
2. **Boltzmann Probability Calculation**:
   - Computes density estimation $\rho(E)$ using `scipy.stats.gaussian_kde`.
   - Calculates Boltzmann weights relative to the minimum energy: $\exp(-\Delta E / k_B T)$.
   - Computes the partition function $Z$ and normalized probabilities.
3. **Energy Extraction**: Reads trajectory files (`traj_0.traj`) via ASE (`ase.io.read`), computes potential energies, normalizes per atom, and adds a global formation energy base offset (`E_global_form_base`).
4. **Area Normalization**: Ensures the integrated probability density for each temperature equals 1 using `scipy.integrate.trapezoid`.
5. **Plotting & Visualization**:
   - Plots curves for multiple temperatures using the `plasma` colormap.
   - Highlights a specific target temperature (`target_temp = 300 K`) with shading under the curve.
   - Places the legend cleanly outside the plot area and saves the high-resolution output as `boltzmann_probabilities_area_norm.png`.

---

## [日本語]

### 概要
このスクリプトは、原子構造のトラジェクトリデータとガウスカーネル密度推定（KDE）を用いて、様々な温度（$T$）におけるボルツマン重み付き確率密度分布を計算し、可視化します。特に、各温度の確率密度曲線について、曲線下の総面積（積分値）が1になるように規格化（面積規格化：台形公式を使用）している点が特徴です。

### 主な機能と処理の流れ
1. **ディレクトリの初期化**: 解析用ディレクトリ（`0_analy/0_xsf_traj`など）を自動作成します。
2. **ボルツマン確率の計算**:
   - `scipy.stats.gaussian_kde` を用いてエネルギーの密度推定 $\rho(E)$ を算出。
   - 最小エネルギーからの相対エネルギーを基準にボルツマン重み $\exp(-\Delta E / k_B T)$ を計算。
   - 分配関数 $Z$ を算出し、規格化された確率を導出。
3. **エネルギーの読み込みと算出**:
   - ASE（`ase.io.read`）を使ってトラジェクトリファイル（`traj_0.traj`）からポテンシャルエネルギーを取得。
   - 原子数で割り、基本形成エネルギーオフセット（`E_global_form_base`）を加えて1原子あたりの形成エネルギーを算出。
4. **面積規格化**:
   - `scipy.integrate.trapezoid`（台形公式）を用いて、各温度における確率密度の積分値（面積）が 1 になるよう規格化。
5. **プロットと可視化**:
   - `plasma` カラーマップを用いて複数温度の曲線をプロット。
   - 指定した目標温度（`target_temp = 300 K`）の曲線下を塗りつぶし（`fill_between`）で強調。
   - 凡例をグラフの外側に配置し、300 DPI の高解像度画像 `boltzmann_probabilities_area_norm.png` として保存。
