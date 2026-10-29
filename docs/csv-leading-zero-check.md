# Keep `000123` intact: a reproducible CSV identifier check before spreadsheet import

A product code such as `000123` can look like a number while actually being an identifier. If an importer converts it to the number `123`, information has been lost. Changing that cell to text afterward does not tell you how many zeros belonged there.

The practical fix is to preserve the source and import identifier columns as text. This article includes a small fictional CSV, a manual workflow, and results from a local Python checker. You can use the workflow without downloading anything from my repository.

**Disclosure:** I publish the linked CSV Guard Free project. AI assisted with the code, tests, and this article. The results below come from executed Python checks on fictional data, not a customer case study. I did not run a native Excel test, and I am not claiming sales, revenue, or measured time savings.

## Why quoting the value is not a complete fix

CSV stores fields and records, not a spreadsheet column's text/number type. Quotation marks help delimit fields; they do not establish a portable “treat this as text” instruction for every importer.

Microsoft documents Excel's automatic removal of leading zeros and recommends handling relevant columns as text during import. Its guidance also covers long numerical identifiers, though the checker in this article does not detect every such case. [Microsoft: keeping leading zeros and large numbers](https://support.microsoft.com/en-au/excel/keeping-leading-zeros-and-large-numbers)

For identifiers, check the actual characters, not just how the cell looks. A display format can make a number look padded without restoring the original source value.

## A five-record example you can inspect yourself

Save the following as `catalog.csv` in UTF-8 using a plain-text editor. All records are fictional. The Chinese headers mean SKU, product name, postal code, and note. The postal-code values are illustrative strings, not validated addresses.

```csv
SKU,商品名,邮编,备注
000123, 帆布收纳袋 ,010001,原创模拟样例
000124,竹制杯垫,010002,NA
000124,竹制杯垫,010002,NA
000125,纸质标签,010003,=1+1
000126, 棉布笔袋 ,010004,
```

There are four things to notice before import:

- Every SKU and postal-code field starts with zero.
- The second and third data records are identical.
- Two product-name fields have spaces at both ends.
- One note begins with `=`. Another is empty, while two contain the literal text `NA`.

The `=1+1` field is an intentionally simple formula-prefix example. Inspect it as text; spreadsheet behavior depends on the application and import route. Do not treat arbitrary formula-like fields from untrusted CSV files as safe merely because this demonstration is harmless.

None of these observations alone authorizes changing the data. An intentional duplicate might represent two separate events. `NA` might be a business code rather than a missing value. Spaces might matter to a downstream system.

## The no-download workflow

For a small file, you can do this manually with your existing text editor and spreadsheet application:

1. **Keep the original untouched.** Work on a copy and inspect it in a plain-text editor first. Confirm that the source still contains `000123`, not `123`.
2. **Identify columns that are labels, not quantities.** Product codes and postal codes in this example should retain their characters. Decide types from their business meaning rather than their appearance.
3. **Import explicitly instead of relying on double-click behavior.** In Excel, use **Data → From Text/CSV**, select the correct encoding and delimiter, then inspect the import settings.
4. **Prevent early numeric conversion.** Where available, disable automatic data-type detection so columns default to text. In **Transform Data/Edit**, confirm the identifier columns have the Text type before loading. If an earlier conversion step has already removed zeros, remove or replace that conversion and return to the original source; merely changing `123` to text is too late.
5. **Verify after loading.** Compare the first SKU with `000123`, the first postal code with `010001`, and confirm there are five data records. Review duplicates, whitespace, and formula-like fields separately before deciding on edits.

These are documentation-based Excel instructions, not an Excel test report. Microsoft describes the Text/CSV connector's encoding, delimiter, and type-detection options, including disabling detection to default columns to Text. Labels and available options vary by host and version. [Microsoft: Text/CSV connector](https://learn.microsoft.com/en-us/power-query/connectors/text-csv)

If you later export another CSV, inspect that exported file too. The next importer still needs the right type settings; CSV does not carry those settings with it.

## What the free checker actually does

[CSV Guard Free](https://github.com/glyahh/csv-guard-free) is an optional local, read-only Python command-line checker. It has no third-party Python dependencies, account requirement, or data-upload step. It reports counts rather than rewriting files. The source is MIT-licensed.

Download the repository using **Code → Download ZIP**, extract it, and open a terminal in the folder containing `demo.py`. With Python 3.10 or later installed, run:

```bash
python demo.py
python -m unittest discover -s tests -v
```

Use `python3` instead of `python` if that is how Python is installed on your system. On Windows, an installed Python Launcher may provide `py`. The executed checks reported here used Linux and Python 3.12.14; Windows and macOS were not tested.

To inspect an authorized local copy of your own file:

```bash
python inspect_csv.py "catalog.csv"
```

For GB18030 input, select that encoding explicitly:

```bash
python inspect_csv.py "catalog.csv" --encoding gb18030
```

`demo.py` and `inspect_csv.py` print a JSON summary; the unittest command prints test results. Some explanatory messages are in Chinese; report field names are in English. No business-data output file is created. If you redirect terminal output yourself, never redirect it to the input filename: shell redirection could overwrite your source before Python reads it.

## Actual results from the supplied sample

The demonstration and test suite were rerun in the Linux environment for this article. The demo completed successfully, and all 14 tests passed. The checks reported:

| Check | Result |
| --- | ---: |
| Data records, excluding the header | 5 |
| Columns | 4 |
| Leading-zero digit cells in column 1: SKU | 5 |
| Leading-zero digit cells in column 3: postal code | 5 |
| Exact duplicate records beyond the first occurrence | 1 |
| Records containing a formula-prefix field | 1 |
| Outer-whitespace cells in column 2: product name | 2 |
| Empty cells in column 4: note | 1 |
| Literal `NA` cells in column 4: note | 2 |

`demo.py` asserts the central counts and compares the input bytes before and after inspection. That comparison passed. It demonstrates that this check did not alter the sample, not that another application will import it correctly.

The tests also cover cases such as invalid encoding, malformed quotes, duplicate headers, inconsistent field counts through the CLI, multiline quoted fields, GB18030 input, oversized files, symlinks, and a POSIX FIFO. Passing these tests is useful evidence for those cases, not proof of compatibility with every CSV producer.

## Read the warnings narrowly

The leading-zero check counts ASCII digit-only strings longer than one character whose first character is `0`. It counts `000123`, but not ` 000123`, `+000123`, or `AB001`. It is not a general identifier detector and does not flag every long number or date-like string.

The formula-prefix check ignores leading whitespace and looks for `=`, `+`, `-`, or `@`. A legitimate negative number can therefore trigger it. A warning is not a malware finding, and a clean report is not a security guarantee. The checker does not execute or neutralize formulas.

Other boundaries matter too:

- Input must be comma-delimited CSV with a nonempty, nonduplicate header and consistent field counts.
- Supported encodings are UTF-8, including a UTF-8 BOM, and explicitly selected GB18030.
- The input limit is 20 MiB. Parsing holds data in memory and can use substantially more memory than the file size. This is not a streaming large-file tool; unusually long fields can hit the standard library's field-size limit.
- It does not handle XLSX, repair damaged files, convert dates or amounts, remove duplicates, or recover zeros already lost upstream.
- Reports omit header names and field values, but include a file SHA-256 and aggregate counts. Do not assume that makes a sensitive report safe to publish.

## The useful stopping point

For this sample, the next action is to import SKU and postal code as text, then verify their exact values. Whether to remove the repeated record, trim product names, or interpret `NA` requires a separate business decision.

You do not need a paid cleaning package to do that. Keep the source, control types at import, and check the result. The optional checker makes a few review candidates visible; it does not replace those decisions.

If you report a problem in the repository's Issues, include your operating system, Python version, encoding, expected behavior, and a fictional minimal example you wrote yourself. Please do not upload real customer records, orders, credentials, or sensitive reports.
