[//]: # (17d1113cb15fe477b6389a6879475c3e7b0d28b6)

# DAML Change Log

## v0.44.6

:star2: **Feature Release**
- `41b20d3a` - Add rules for release label pipeline workflow and merge request release template

:tools: **Improvements and Enhancements**
- `7ee53c9c` - Update Divergence default to MST

## v0.44.2

:tools: **Improvements and Enhancements**
- `1468aa5c` - Switch to markdown and updated docs

## v0.43.0

:tools: **Improvements and Enhancements**
- `670a0db5` - Add support for classwise Sufficiency metrics
- `b96ee099` - Have sufficiency train and eval functions take indices and batch size instead of a DataLoader

## v0.42.2

:tools: **Improvements and Enhancements**
- `5225c491` - Change output classes to dictionaries
- `45040682` - Make Sufficiency a stateful class and revise SufficiencyOutput
- `7c5fdcff` - Pass method as a parameter to determine metric algorithm to use
- `2e883f6d` - Add better optimizer to find global minimum
- `c3c78680` - Expose AETrainer to public API to use model multiple times after training

:space_invader: **Fixes**
- `93564b95` - Updating pyproject.toml and lock file to set dependency less than numpy 2.0

## v0.42.0

:tools: **Improvements and Enhancements**
- `601cfae8` - Sufficiency Plotting of Multiple Metrics during one run
- `3d68a6f1` - Add parameter to plot function for optional file output

:construction: **Deprecations and Removals**
- `a6ce3e72` - Remove UAP_MST metric

## v0.40.2

:tools: **Improvements and Enhancements**
- `f3eddaed` - Flavor 2 - Remove models from metrics entirely

## v0.40.1

:construction: **Deprecations and Removals**
- `db888bb7` - Remove usage of DamlDataset for ARiA metrics

## v0.38.1

:tools: **Improvements and Enhancements**
- `42617f43` - Enable GPU functionality in pytorch features

## v0.38.0

:star2: **Feature Release**
- `c9b5116e` - ARiA Autoencoder as PyTorch Model

:tools: **Improvements and Enhancements**
- `8fe97232` - Add export_model functionality and improve test coverage
- `42cc77ea` - Add empirical upper bound to UAP metric output

:space_invader: **Fixes**
- `636dfdaf` - update project with __version__ metadata

## v0.36.1

:star2: **Feature Release**
- `7d1a599f` - Implement the uap class

## v0.36.0

:tools: **Improvements and Enhancements**
- `0799523b` - Object detection model training

## v0.29.0

:star2: **Feature Release**
- `166df3b0` - Implement Dataset Sufficiency Metric

:tools: **Improvements and Enhancements**
- `5c4e6e06` - Use convolutional autoencoder for BER and Divergence metrics

:space_invader: **Fixes**
- `c78e5502` - Sufficiency typecheck bugfix

## v0.28.5

:tools: **Improvements and Enhancements**
- `9d1c354c` - Add fit_dataset, format_dataset to DpDivergence & BER

## v0.28.4

:space_invader: **Fixes**
- `c39e009e` - Fix typecheck issues found with pyright-1.1.333

## v0.26.13

:star2: **Feature Release**
- `949e09bd` - Add kNN BER implementation

## v0.26.10

:tools: **Improvements and Enhancements**
- `dab0a8ff` - Handle MST edge cases

## v0.26.4

:tools: **Improvements and Enhancements**
- `bf31996f` - BER lower bound capability

## v0.25.11

:tools: **Improvements and Enhancements**
- `dfe0bddb` - Add support for python 3.11

## v0.25.4

:tools: **Improvements and Enhancements**
- `2ca285cc` - update BER metric to return a dataclass instead of dict

## v0.25.3

:space_invader: **Fixes**
- `67f08b27` - Fix: Alibi-detect-models-have-fixed-architecture-shapes

## v0.25.2

:tools: **Improvements and Enhancements**
- `db4adaff` - 69 convert metric output dictionary to dataclass

## v0.24.8

:star2: **Feature Release**
- `79614577` - Implement Multiclass MST version of BER

## v0.24.6

:star2: **Feature Release**
- `2ad9fed5` - Implement BER estimate

## v0.23.1

:star2: **Feature Release**
- `99d2fd22` - Implement outlier detection metrics using the alibi-detect VAE method

## v0.23.0

:star2: **Feature Release**
- `85eb2c1f` - Implement outlier detection metrics using the alibi-detect auto-encoder method
