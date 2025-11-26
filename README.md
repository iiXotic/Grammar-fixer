# Advanced File Scanner 🕷️

A powerful file scanner with real-time monitoring and VirusTotal integration to keep your system clean.

## App Screenshot

---

## Why?

Standard antivirus software can be heavy and slow. This tool is lightweight, fast, and gives you control over your system's security.

---

## Features

- **Scan on Demand:** Scan any directory to detect suspicious files based on a heuristic scoring system.
- **Real-Time Monitoring:** Actively monitors a selected directory for any new or modified files, alerting you immediately of potential threats.
- **VirusTotal Integration:** For a deeper analysis, you can enable VirusTotal scanning to check files against dozens of antivirus engines.
- **Quarantine and Whitelist:** Isolate suspicious files in a quarantine zone or add trusted files to a whitelist to prevent future alerts.
- **Modern UI:** Built with CustomTkinter for a clean and intuitive user experience.

---

## How to Use

### Scanning a Directory:
1.  Click the **Browse** button to select the directory you want to scan.
2.  Enable **VirusTotal Scan** for a more thorough (but slower) scan.
3.  Click **Start Scan** to begin.

### Real-Time Monitoring:
1.  Select the directory you want to monitor.
2.  Enable the **Real-time Monitor** checkbox.
3.  The application will now monitor the selected directory for any changes and alert you of suspicious files.

### Managing Results:
-   After a scan, suspicious files will be listed in the results area.
-   You can choose to **Quarantine** a file to isolate it or **Whitelist** it if you trust it.

---

## Installation

1.  Download the latest release from the Releases tab.

2.  Get a free API key from [VirusTotal](https://www.virustotal.com/).

3.  Create a `.env` file next to the `.exe` and paste your key:
    ```
    VT_API_KEY=your_key_here
    ```

4.  Run `AdvancedFileScanner.exe`.
