# jdg-auto-invoice

When the form (https://tally.so/r/mYOOX6) receives a submission it adds it to a Google Sheets (by itself).

This script runs every 10 mins to check if has been added. When it happens, the invoice is generated from the `invoice.tex` into a pdf (with custom content to match the form submission) and the signature (from the form) is downloaded, then both of theses are uploaded into a new folders in the GDrive and sent by email along with the void cheque. After that it updates the form so that it won't be recognized again by the script.
