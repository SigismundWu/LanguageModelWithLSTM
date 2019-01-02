# AZJ Rating

## Requirements

* Python 3.6+

## How to install

```console
$ pip install azj_rating-1.0.1.tar.gz
```

## How to use

```text
Including 3 sub-commands:

usage: azj_rating [-h] {normal,FAM,FAM_airflow} ...

Calculating star rating for teachers using QC and behavior data.

positional arguments:
  {normal,FAM,FAM_airflow}
                        Use the different mode,'normal', 'FAM' or
                        'FAM_airflow'
    normal              normal_mode
    FAM                 FAM_mode, use the FAM to process data
    FAM_airflow         FAM_mode, airflow deploy ready

optional arguments:
  -h, --help            show this help message and exit


Sub-commands "normal":

usage: azj_rating normal [-h] [--output OUTPUT]
                         [--min_qc_scores MIN_QC_SCORES]
                         [--coefficient COEFFICIENT]
                         mode teacher_star_data star_rate_data

positional arguments:
  mode                  with_total_score or origin
  teacher_star_data     Teacher star data json file path
  star_rate_data        Path to star_rate standard data json file

optional arguments:
  -h, --help            show this help message and exit
  --output OUTPUT       Output data. The standard output is default. With
                        FA_Model, please use the csv format
  --min_qc_scores MIN_QC_SCORES
                        Minimum count of QC scores for each teacher [5]
  --coefficient COEFFICIENT
                        Standardize the QC scores for calculating the total
                        scores [0.005]


Sub-commands FAM:

usage: azj_rating FAM [-h] [--output OUTPUT] data_path

positional arguments:
  data_path        Six data of teacher star data, including star rate

optional arguments:
  -h, --help       show this help message and exit
  --output OUTPUT  Output data. The standard output is default. With FA_Model,
                   please use the csv format


Sub-commands FAM_airflow:

usage: azj_rating FAM_airflow [-h] conn_info teacher_star_vars

positional arguments:
  conn_info          Path of a json file contains conn_info of the databases
  teacher_star_vars  Path of an json object contains data path

optional arguments:
  -h, --help         show this help message and exit

```

## Development

```console
$ pip install -r requirements.txt
```

## Test

```console
$ python -m unittest
```

## Links

* [unittest — Unit testing framework](https://docs.python.org/3/library/unittest.html)
* [argparse — Parser for command-line options, arguments and sub-commands](https://docs.python.org/3/library/argparse.html)
