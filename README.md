# Data-Analysis Metrics Library (DAML)

## About DAML

The Data-Analysis Metrics Library, or DAML, focuses on characterizing image data and its impact on model performance across classification and object-detection tasks.

**Model-agnostic metrics that bound real-world performance**
- relevance/completeness/coverage
- metafeatures (data complexity)

**Model-specific metrics that guide model selection and training**
- dataset sufficiency
- data/model complexity mismatch

**Metrics for post-deployment monitoring of data with bounds on model performance to guide retraining**
- dataset-shift metrics
- model performance bounds under covariate shift
- guidance on sampling to assess model error and model retraining

## Getting Started

### Installing DAML

To install the package from the GitLab Pypi repository, run the following command in an environment with Python 3.8-3.11 installed:

`pip install daml --index-url https://gitlab.jatic.net/api/v4/projects/151/packages/pypi/simple`

If you would like to enable outlier-detection using the alibi-detect package, install DAML with the extra `alibi-detect` specified:

`pip install daml[alibi-detect] --index-url https://gitlab.jatic.net/api/v4/projects/151/packages/pypi/simple`

### Additional Tutorials
For more ideas on getting started using DAML in your workflow, additional information is in our Sphinx documentation hosted in [here](https://jatic.pages.jatic.net/aria/daml/) on Gitlab Pages.

## Contributing
For steps on how to get started on contributing to the project, you can follow the steps in [CONTRIBUTING.md](CONTRIBUTING.md).

## POCs
- **POC**: Scott Swan @scott.swan
- **DPOC**: Andrew Weng @aweng
