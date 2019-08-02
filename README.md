# ScienceBeam Utils

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Provides utility functions related to the [ScienceBeam](https://github.com/elifesciences/sciencebeam) project.

Please refer to the [development documentation](https://github.com/elifesciences/sciencebeam-utils/blob/develop/doc/development.md)
if you wish to contribute to the project.

Most tools are not yet documented. Please feel free to browse the code or tests or ask raise an issue.

## Pre-requisites

- Python 2.7 or 3 (Apache Beam may not fully support Python 3 yet)
- [Apache Beam](https://beam.apache.org/)

[Apache Beam](https://beam.apache.org/) may be used to for preprocessing but also its transparent FileSystems API which makes it easy to access files in the cloud.

## Install

```bash
pip install apache_beam[gcp]
```

```bash
pip install sciencebeam-utils
```

## CLI Tools

### Find File Pairs

The preferred input layout is a directory containing a gzipped pdf (`.pdf.gz`) and gzipped xml (`.nxml.gz`), e.g.:

- manuscript_1/
  - manuscript_1.pdf.gz
  - manuscript_1.nxml.gz
- manuscript_2/
  - manuscript_2.pdf.gz
  - manuscript_2.nxml.gz

Using compressed files is optional but recommended to reduce file storage cost.

The parent directory per manuscript is optional. If that is not the case then the name before the extension must be identical (which is recommended in general).

Run:

```bash
python -m sciencebeam_utils.tools.find_file_pairs \
--data-path <source directory> \
--source-pattern *.pdf.gz --xml-pattern *.nxml.gz \
--out <output file list csv/tsv>
```

e.g.:

```bash
python -m sciencebeam_utils.tools.find_file_pairs \
--data-path gs://some-bucket/some-dataset \
--source-pattern *.pdf.gz --xml-pattern *.nxml.gz \
--out gs://some-bucket/some-dataset/file-list.tsv
```

That will create the TSV (tab separated) file `file-list.tsv` with the following columns:

- _source_url_
- _xml_url_

That file could also be generated using any other preferred method.

### Split File List

To separate the file list into a _training_, _validation_ and _test_ dataset, the following script can be used:

```bash
python -m sciencebeam_utils.tools.split_csv_dataset \
--input <csv/tsv file list> \
--train 0.5 --validation 0.2 --test 0.3 --random --fill
```

e.g.:

```bash
python -m sciencebeam_utils.tools.split_csv_dataset \
--input gs://some-bucket/some-dataset/file-list.tsv \
--train 0.5 --validation 0.2 --test 0.3 --random --fill
```

That will create three separate files in the same directory:

- `file-list-train.tsv`
- `file-list-validation.tsv`
- `file-list-test.tsv`

The file pairs will be randomly selected (_--random_) and one group will also include all remaining file pairs that wouldn't get include due to rounding (_--fill_).

As with the previous step, you may decide to use your own process instead.

Note: those files shouldn't change anymore once you used those files

### Get Output Files

Since ScienceBeam is intended to convert files, there will be output files. To make it specific what the filenames are,
the output files are also kept in a file list. This tool will generate the file list (it doesn't matter whether the files actually exist for this purpose).

e.g.

```bash
python -m sciencebeam_utils.tools.get_output_files \
  --source-file-list path/to/source/file-list-train.tsv \
  --source-file-column=source_url \
  --output-file-suffix=.xml \
  --output-file-list path/to/results/file-list.lst
```

By adding the `--check` argument, it will check whether the output files exist (see below).

### Check File List

After generating an output file list, this tool can be used whether the output files exist or are complete.

e.g.

```bash
python -m sciencebeam_utils.tools.check_file_list \
  --file-list path/to/results/file-list.lst \
  --file-column=source_url \
  --limit=100
```

This will check the first 100 output files and report on it. The command will fail if none of the output files exist.
