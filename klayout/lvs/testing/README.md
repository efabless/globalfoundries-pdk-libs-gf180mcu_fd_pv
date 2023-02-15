# Globalfoundries 180nm MCU LVS Testing

Explains how to test GF180nm LVS rule decks.

## Folder Structure

```text
📁 testing
 ┣ 📜Makefile
 ┣ 📜README.md
 ┣ 📜run_regression.py
 ┣ 📜extraction_checking
 ┗ 📜testcases
 ```

## Prerequisites

At a minimum:

- Git 2.35+
- Python 3.6+
- KLayout 0.28.4+

## Usage

To make a full test for GF180nm LVS rule deck, you could use the following command in testing directory:

```bash
make all
```

## **Regression Outputs**

- Final results will appear at the end of the run logs.
