# Sample Output

Command:

```powershell
python -m fileguard.main preview --path ./demo_files/messy_downloads --rules-only
```

Example output:

```text
Plan ID: plan_20260702_120931
Files scanned: 10
Classification mode: rules-only
Claude available: no
Claude calls used: 0 / 50
Claude classifications: 0
Rule classifications: 10
Rule fallbacks: 0

- C:\path\to\fileguard\demo_files\messy_downloads\Kalyaan_Resume_Final.pdf
  -> Organized\Documents\PDFs\Resumes\Kalyaan_Resume_Final.pdf
  classifier: rules
  confidence: 0.90
  reason: Matched extension .pdf to Documents/PDFs; Matched keyword 'resume' for Resumes
- C:\path\to\fileguard\demo_files\messy_downloads\random_download.bin
  -> Organized\Review Needed\Misc\random_download.bin
  classifier: rules
  confidence: 0.30
  reason: Unknown extension: .bin; No filename keyword matched within Review Needed

Dry run only. No files were moved.
```

