# ODI Cricket Analytics GUI (Batting + Bowling)

## Project layout
```
ODI_Cricket_GUI/
  gui.py                 # Tkinter application (run this)
  odi_analysis.py        # ODIAnalysis  - batting class (your original code + new methods)
  odi_bowling.py         # ODIBowlingAnalysis - bowling class (same style as the batting one)
  requirements.txt
  notebooks/
    Python_Course_Project_original.ipynb   # your original batting notebook (untouched)
    ODI_Batting_Analysis.ipynb             # batting class with the new methods
    ODI_Bowling_Analysis.ipynb             # bowling class with the new methods
```

## Run locally (Windows / VS Code)
1. Install Python 3.10+ (Tkinter comes with the standard Windows installer).
2. Open this folder in VS Code.
3. In terminal: `pip install -r requirements.txt`
4. Run: `python gui.py`
5. Click **Open CSV** and choose your original `ODI.csv` file (the full file, 171,968 rows). Batting and bowling are both loaded from this one file.

<table>
  <tr>
    <td align="center">
      <a href="https://i.postimg.cc/DZVkWMFW/Screenshot-2026-10-30-215646.png">
        <img src="https://i.postimg.cc/DZVkWMFW/Screenshot-2026-10-30-215646.png" width="100%" alt="Screenshot 1">
      </a>
      <br><sub><b>Main menu / main screen (showing "Choose your ODI.csv file to begin").</b></sub>
    </td>
    <td align="center">
      <a href="https://i.postimg.cc/pTNb96xn/Screenshot-2026-10-30-215824.png">
        <img src="https://i.postimg.cc/pTNb96xn/Screenshot-2026-10-30-215824.png" width="100%" alt="Screenshot 2">
      </a>
      <br><sub><b>Dashboard view after loading CSV (showing metric cards like "Total Wickets", "Average Economy Rate").</b></sub>
    </td>
  </tr>
  <tr>
    <td align="center">
      <a href="https://i.postimg.cc/qRfVt503/Screenshot-2026-10-30-215920.png">
        <img src="https://i.postimg.cc/qRfVt503/Screenshot-2026-10-30-215920.png" width="100%" alt="Screenshot 3">
      </a>
      <br><sub><b>Player Explorer: Searching for "V Kohli" or "M Muralitharan" and displaying the summary text box.</b></sub>
    </td>
    <td align="center">
      <a href="https://i.postimg.cc/G20wB5rY/Screenshot-2026-10-30-215947.png">
        <img src="https://i.postimg.cc/G20wB5rY/Screenshot-2026-10-30-215947.png" width="100%" alt="Screenshot 4">
      </a>
      <br><sub><b>Charts tab: Displaying a horizontal bar chart of "Top 10 career run scorers" or "Average economy rate by year".</b></sub>
    </td>
  </tr>
  <tr>
    <td align="center">
      <a href="https://i.postimg.cc/wvK8tGHN/Screenshot-2026-10-30-220027.png">
        <img src="https://i.postimg.cc/wvK8tGHN/Screenshot-2026-10-30-220027.png" width="100%" alt="Screenshot 5">
      </a>
      <br><sub><b>Dataset Browser: Filtering records by typing a player's name and clicking "Filter by Player".</b></sub>
    </td>
    <td align="center">
      <a href="https://i.postimg.cc/RFr53D9w/Screenshot-2026-10-30-220124.png">
        <img src="https://i.postimg.cc/RFr53D9w/Screenshot-2026-10-30-220124.png" width="100%" alt="Screenshot 6">
      </a>
      <br><sub><b>Error handling example: Messagebox showing "Dataset needed" when trying to draw a chart before loading a file.</b></sub>
    </td>
  </tr>
  <tr>
    <td align="center" colspan="2">
      <a href="https://i.postimg.cc/mDxfc5RQ/Screenshot-2026-10-30-220303.png">
        <img src="https://i.postimg.cc/mDxfc5RQ/Screenshot-2026-10-30-220303.png" width="50%" alt="Screenshot 7">
      </a>
      <br><sub><b>Saved data file contents (e.g., the exported odi_batting_records.csv opened in Excel).</b></sub>
    </td>
  </tr>
</table>
