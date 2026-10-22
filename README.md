# AMCs-NAVs-FinTech-Analysis

Analysis of Net Asset Values (NAVs) of Asset Management Companies (AMCs) in the Indian mutual fund sector using historical financial data. This project focuses on exploring, processing, combining, and analyzing NAV records to identify fund performance trends and derive meaningful financial insights.

## Project Overview

This project focuses on analyzing approximately **40 million historical financial records** from CAMS and KFINTECH to identify potentially profitable mutual funds in the Indian mutual fund market. The primary challenge is transforming large volumes of raw NAV (Net Asset Value) data into a structured, efficient, and analytically useful dataset.

The workflow involves exploratory data analysis, data extraction, format conversion, dataset consolidation, and performance-based filtering. The processed records are stored in Parquet format to enable efficient querying and analysis. Fund performance is evaluated using historical returns and other relevant metrics to filter and identify funds that meet selected profitability criteria.

The project demonstrates the practical application of Python-based data engineering and financial analytics to a large-scale dataset, converting millions of raw records into actionable insights for mutual fund performance analysis.

## Key Highlights

- **Large-Scale Data Processing:** Worked with approximately 40 million historical financial records from CAMS and KFINTECH.
- **Data Engineering Pipeline:** Performed data exploration, extraction, format conversion, and dataset consolidation.
- **Efficient Storage:** Used Parquet columnar storage to support efficient analytical workflows.
- **Performance-Based Filtering:** Applied historical return and risk metrics to narrow down funds meeting selected performance criteria.
- **Financial Analytics:** Analyzed historical NAV trends to identify and compare potentially profitable mutual funds.

## Final Analysis Notebook — Top NAVs

The final stage of the project focuses on identifying historically high-performing mutual funds using processed NAV data and performance-based filtering criteria.

**[View Top_NAVs.ipynb on Google Colab](https://colab.research.google.com/drive/19oKzfbknaHRYcL_BSSkx_l1CrBGUZWjA?usp=sharing)**

The notebook showcases the final analysis, including the evaluation of historical fund performance and the application of criteria to identify funds meeting selected return and investment-duration thresholds. It provides a view-only demonstration of the project's analytical results.

## Repository Structure

```text
AMCs-NAVs-FinTech-Analysis/
├── dataset/
│   ├── combined/
│   │   ├── final_combined.parquet
│   │   └── returns.parquet
│   └── Kfintech AMCs NAVs 09052025/
│   └── CAMS AMCs NAVs 09052025/
│
├── notebooks/
│   ├── 1_initial_dataset_1_EDA.ipynb
│   ├── 2_dataset_1_conversion_test.ipynb
│   ├── 3_dataset_1_extraction.ipynb
│   ├── 4_combine_dataset_1_parquets.ipynb
│   ├── 5_dataset_2_EDA.ipynb
│   ├── 6_dataset_2_extraction.ipynb
│   ├── 7_combined_analysis.ipynb
│   ├── 8_filtered_nav_analysis.ipynb
│   └── Top_NAVs.ipynb
│
├── src/
├── .gitignore
├── .python-version
├── LICENSE
├── pyproject.toml
├── README.md
└── uv.lock
```

## Dataset

The project uses publicly available historical Net Asset Value (NAV) records from CAMS and KFINTECH, two sources of Indian mutual fund data.

The original data was distributed in **DBF (dBASE) format**, rather than in analysis-ready CSV or Parquet files. The CAMS dataset was provided as a single DBF file, while the KFINTECH dataset was distributed across 54 DBF files. Together, the raw data occupied approximately 11 GB, presenting a substantial data-processing challenge.

The datasets contain historical NAV values and associated financial metadata. Before meaningful analysis could be performed, the raw files had to be explored, extracted, converted into a more efficient storage format, and consolidated into structured datasets.

The processed data is stored in **Parquet format**, enabling efficient analytical queries and supporting the subsequent filtering and evaluation of mutual funds based on historical performance.

### Processed datasets

| File | Purpose |
|---|---|
| `final_combined.parquet` | Consolidated NAV dataset for analysis |
| `returns.parquet` | Dataset containing fund-level return and performance analytics |

The `dataset/combined/` directory contains the processed datasets used in the later stages of the analysis.

## Dataset Setup

Before running the notebooks:

1. Obtain the original dataset archives.
2. Extract the two ZIP archives into separate folders inside the `dataset/` directory.
3. Ensure the extracted folder names and file locations match the paths expected by the notebooks.
4. Run the notebooks in the order described below.

**Note:** The raw datasets are not necessarily included in the repository. Ensure you have access to the original files before running the data-processing notebooks.

## Analysis Workflow

The notebooks are organized into stages that follow the dataset-processing pipeline.

| Notebook | Purpose |
|---|---|
| `1_initial_dataset_1_EDA.ipynb` | Initial exploratory data analysis of the first dataset |
| `2_dataset_1_conversion_test.ipynb` | Testing dataset format conversion |
| `3_dataset_1_extraction.ipynb` | Extracting and processing the first dataset |
| `4_combine_dataset_1_parquets.ipynb` | Combining processed Parquet files |
| `5_dataset_2_EDA.ipynb` | Exploratory data analysis of the second dataset |
| `6_dataset_2_extraction.ipynb` | Extracting and processing the second dataset |
| `7_combined_analysis.ipynb` | Analysis of the combined datasets |
| `8_filtered_nav_analysis.ipynb` | Analysis of filtered NAV records |
| `Top_NAVs.ipynb` | Analysis of NAV-based fund performance and top-performing funds. This notebook is hosted on Google Colab and publicly available in view-only mode. |

The recommended workflow is to begin with data exploration, proceed through extraction and conversion, combine the processed datasets, and then perform the final analyses.

## Technologies Used

- **Jupyter Notebook** — Exploratory data analysis and step-by-step data processing
- **dbfread** — Reading and extracting records from DBF files
- **Pandas** — Data manipulation, filtering, grouping, sorting, and NAV analysis
- **NumPy** — Numerical computations and financial metric calculations
- **PyArrow** — Parquet serialization and columnar data storage
- **Matplotlib** — Visualizing NAV trends and fund performance
- **Parquet** — Efficient storage of processed financial datasets
- **uv** — Python project and dependency management

## Getting Started

### Prerequisites

Install Python and [uv](https://docs.astral.sh/uv/).

### Installation

Clone the repository:

```bash
git clone https://github.com/<your-username>/AMCs-NAVs-FinTech-Analysis.git
cd AMCs-NAVs-FinTech-Analysis
```

Install the project dependencies:

```bash
uv sync
```

Launch Jupyter Notebook using the configured project environment:

```bash
uv run jupyter notebook
```

Open the `notebooks/` directory and execute the notebooks in the recommended order.

If Jupyter Notebook is not included in the project dependencies, install it in the project environment before launching it.

## Objectives

- Explore historical NAV data from multiple registrars.
- Convert and consolidate financial datasets into an efficient analytical format.
- Analyze historical NAV movements and fund performance.
- Filter funds based on selected performance criteria.
- Identify and compare potentially high-performing funds using historical data.

## Future Scope

The processed datasets and analytical results can serve as the foundation for a FinTech application that provides an interactive interface for exploring mutual funds, visualizing historical NAV trends, comparing performance metrics, and examining investment risk.

## Disclaimer

This project is intended for educational, research, and analytical purposes. Historical NAV performance does not guarantee future returns. The analyses presented here should not be considered financial advice or investment recommendations.

## License

See the [LICENSE](LICENSE) file for licensing information.