# Globalfoundries 180nm MCU LVS Testing

Explains how to test GF180nm LVS rule deck.

## Folder Structure

```text
📦testing
 ┣ 📜Makefile
 ┣ 📜README.md
 ┣ 📜run_regression.py
 ┣ 📜extraction_checking
 ┗ 📜testcases
 ┗ 📜man_testcases
 ```

## Prerequisites

At a minimum:

- Git 2.35+
- Python 3.6+
- KLayout 0.28.0+

### On Ubuntu, you can just

`apt install -y build-essential python3`

- Check this [Klayout](https://www.klayout.de/) for klayout installation.

## Regression Usage

To make a full test for GF180nm LVS rule deck, you could use the following command in testing directory:

```bash
make all
```

- You could also check LVS extraction for each device individually, using the following command will list the valid targets in Makefile:

    ```bash
    make help
    ```

## **Regression Outputs**

- Final results will appear at the end of the run logs.
