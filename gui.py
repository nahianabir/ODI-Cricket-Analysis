"""Tkinter interface layered on top of the ODIAnalysis (batting) and ODIBowlingAnalysis (bowling) classes."""

# ---------------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------------
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from odi_analysis import ODIAnalysis
from odi_bowling import ODIBowlingAnalysis


# ---------------------------------------------------------------
# COLOURS (change them here and the whole app changes)
# ---------------------------------------------------------------
BG = '#101827'        # main background
PANEL = '#192538'     # cards, tables and chart background
FG = '#eef4ff'        # normal text
MUTED = '#aabbd1'     # light grey text
ACCENT = '#41c6a5'    # green highlight
BTN = '#237b79'       # button colour
BTN_OFF = '#2b4059'   # button colour when it is not selected


# ---------------------------------------------------------------
# SMALL HELPER FUNCTIONS (used many times below)
# ---------------------------------------------------------------
def label(parent, text, size=11, color=FG, bold=False):
    """Make a text label with the app's font and colours."""
    if bold:
        weight = 'bold'
    else:
        weight = 'normal'

    return tk.Label(parent,
                    text=text,
                    bg=parent.cget('bg'),      # use the same background as the parent
                    fg=color,
                    font=('Segoe UI', size, weight))


def button(parent, text, command, color=BTN):
    """Make a flat coloured button. 'command' is the function that runs on click."""
    return tk.Button(parent,
                     text=text,
                     command=command,
                     bg=color,
                     fg='white',
                     activebackground=ACCENT,
                     activeforeground='#0c1827',
                     relief='flat',
                     font=('Segoe UI', 10, 'bold'),
                     padx=15,
                     pady=9,
                     cursor='hand2')


def make_tree(parent, cols, height, side=None):
    """Make a table (Treeview) with a vertical and a horizontal scrollbar."""
    # a frame to hold the table and its scrollbars
    frame = tk.Frame(parent, bg=BG)
    if side:
        frame.pack(side=side, fill='both', expand=True, padx=(0, 8))
    else:
        frame.pack(fill='both', expand=True)

    # the table itself
    tree = ttk.Treeview(frame, columns=cols, show='headings', height=height)

    # set the heading and width of every column
    for c in cols:
        tree.heading(c, text=c)
        if c == 'Player':
            column_width = 175      # player names need more space
        else:
            column_width = 115
        tree.column(c, width=column_width, anchor='w')

    # scrollbars
    scroll_y = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
    scroll_x = ttk.Scrollbar(frame, orient='horizontal', command=tree.xview)
    tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

    # place the table and scrollbars in a grid
    tree.grid(row=0, column=0, sticky='nsew')
    scroll_y.grid(row=0, column=1, sticky='ns')
    scroll_x.grid(row=1, column=0, sticky='ew')

    # let the table stretch when the window is resized
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)
    return tree


def fmt(value):
    """Make a value look nice: 8.0 becomes 8, and an empty value becomes a dash."""
    if pd.isna(value):
        return '—'
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


# ---------------------------------------------------------------
# AnalysisPage : the parts that Batting and Bowling share
# ---------------------------------------------------------------
class AnalysisPage(tk.Frame):
    """Common page (Dashboard / Player Explorer / Dataset Browser). Batting and Bowling pages fill in the details."""

    # These are empty here. BattingPage and BowlingPage fill them in with their own values.
    name = ''
    metric_names = []
    cards_per_row = 3
    tables = []          # (title, columns)
    record_cols = []     # (heading, dataframe column)
    charts = {}          # chart title: (analysis method, 'bar' or 'line', axis label)
    required = set()

    def __init__(self, parent, status):
        super().__init__(parent, bg=BG)
        self.status = status         # the status bar text at the bottom of the window
        self.analysis = None         # will hold the analysis object once a CSV is loaded
        self.filtered = None         # will hold the records shown in the Dataset Browser

        # the tabs (Dashboard, Player Explorer, Charts, Dataset Browser)
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill='both', expand=True)

        # one frame for the inside of each tab
        self.dashboard = tk.Frame(self.tabs, bg=BG)
        self.players = tk.Frame(self.tabs, bg=BG)
        self.charts_tab = tk.Frame(self.tabs, bg=BG)
        self.records = tk.Frame(self.tabs, bg=BG)

        self.tabs.add(self.dashboard, text='  Dashboard  ')
        self.tabs.add(self.players, text='  Player Explorer  ')
        self.tabs.add(self.charts_tab, text='  Charts  ')
        self.tabs.add(self.records, text='  Dataset Browser  ')

        # draw the inside of each tab
        self.build_dashboard()
        self.build_players()
        self.build_charts()
        self.build_records()

    # ---- building the screens ----
    def build_dashboard(self):
        """Dashboard tab: number cards on top, small tables below."""
        label(self.dashboard, f'ODI {self.name.lower()} overview', 16, bold=True).pack(anchor='w', pady=(6, 15))

        # frame that holds all the number cards
        cards = tk.Frame(self.dashboard, bg=BG)
        cards.pack(fill='x')

        # metric_vars keeps the text of every card so we can change it later
        self.metric_vars = {}
        for i, name in enumerate(self.metric_names):
            card = tk.Frame(cards, bg=PANEL, padx=15, pady=13)

            # i // cards_per_row = which row, i % cards_per_row = which column
            card_row = i // self.cards_per_row
            card_column = i % self.cards_per_row
            card.grid(row=card_row, column=card_column, padx=5, pady=5, sticky='nsew')

            label(card, name, 10, MUTED).pack(anchor='w')

            card_text = tk.StringVar(value='—')
            self.metric_vars[name] = card_text
            tk.Label(card, textvariable=card_text, bg=PANEL, fg=ACCENT, font=('Segoe UI', 18, 'bold')).pack(anchor='w', pady=5)

        # make all card columns the same width
        for i in range(self.cards_per_row):
            cards.columnconfigure(i, weight=1)

        # area below the cards that holds the small tables side by side
        area = tk.Frame(self.dashboard, bg=BG)
        area.pack(fill='both', expand=True, pady=(14, 0))

        self.table_trees = []
        for title, cols in self.tables:
            block = tk.Frame(area, bg=BG)
            block.pack(side='left', fill='both', expand=True, padx=4)
            label(block, title, 14, bold=True).pack(anchor='w', pady=(0, 8))
            self.table_trees.append(make_tree(block, cols, height=6))

        button(self.dashboard, 'Refresh Statistics', self.refresh).pack(anchor='e', pady=10)

    def build_players(self):
        """Player Explorer tab: search box, button and a text area for the result."""
        label(self.players, f'Individual {self.name.lower()} summary', 16, bold=True).pack(anchor='w', pady=(6, 15))

        # row with the search box and the button
        bar = tk.Frame(self.players, bg=BG)
        bar.pack(fill='x')

        self.player_name = tk.StringVar()
        self.player_combo = ttk.Combobox(bar, textvariable=self.player_name, width=48)
        self.player_combo.pack(side='left', padx=(0, 10), ipady=5)

        # pressing Enter in the box does the same as clicking "Search Player"
        self.player_combo.bind('<Return>', lambda e: self.search_player())
        button(bar, 'Search Player', self.search_player).pack(side='left')

        # text area that shows the player's summary (read only)
        self.player_output = tk.Text(self.players,
                                     height=14,
                                     bg=PANEL,
                                     fg=FG,
                                     insertbackground=FG,
                                     relief='flat',
                                     font=('Consolas', 13),
                                     padx=22,
                                     pady=20,
                                     state='disabled')
        self.player_output.pack(fill='both', expand=True, pady=20)

    def build_charts(self):
        """Charts tab: a drop-down to choose a chart and the chart picture itself."""
        label(self.charts_tab, f'{self.name} charts', 16, bold=True).pack(anchor='w', pady=(6, 15))

        # row with the drop-down and buttons
        bar = tk.Frame(self.charts_tab, bg=BG)
        bar.pack(fill='x')

        # the first chart in the list is selected at the start
        self.chart_name = tk.StringVar(value=list(self.charts)[0])
        combo = ttk.Combobox(bar, textvariable=self.chart_name, values=list(self.charts), width=48, state='readonly')
        combo.pack(side='left', padx=(0, 10), ipady=5)

        # draw the chart again when a new one is chosen from the drop-down
        combo.bind('<<ComboboxSelected>>', lambda e: self.draw_chart())

        button(bar, 'Draw Chart', self.draw_chart).pack(side='left')
        button(bar, 'Save Image', self.save_chart).pack(side='right')

        # matplotlib figure placed inside the tkinter window
        self.figure = Figure(figsize=(9, 5), dpi=100, facecolor=PANEL)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.charts_tab)
        self.canvas.get_tk_widget().pack(fill='both', expand=True, pady=14)

    def build_records(self):
        """Dataset Browser tab: filter box, buttons and a big table of records."""
        label(self.records, f'Explore and export {self.name.lower()} records', 16, bold=True).pack(anchor='w', pady=(6, 12))

        # row with the filter box and buttons
        bar = tk.Frame(self.records, bg=BG)
        bar.pack(fill='x', pady=(0, 10))

        self.filter_text = tk.StringVar()
        entry = tk.Entry(bar, textvariable=self.filter_text, width=34, font=('Segoe UI', 11))
        entry.pack(side='left', ipady=7, padx=(0, 10))

        # pressing Enter in the box does the same as clicking "Filter by Player"
        entry.bind('<Return>', lambda e: self.filter_records())

        button(bar, 'Filter by Player', self.filter_records).pack(side='left', padx=(0, 8))
        button(bar, 'Clear Filter', self.clear_filter).pack(side='left', padx=(0, 8))
        button(bar, 'Export CSV', self.export_csv).pack(side='right')

        # the table headings come from record_cols (first item of every pair)
        headings = []
        for heading, column in self.record_cols:
            headings.append(heading)
        self.record_tree = make_tree(self.records, headings, height=15)

        self.record_count = label(self.records, 'No data loaded', 10, MUTED)
        self.record_count.pack(anchor='w', pady=8)

    # ---- loading ----
    def load(self, path):
        """Create the analysis object and check it. Raises ValueError if the file does not fit."""
        obj = self.analysis_class(path)

        # check that every column we need is in the file
        missing = self.required - set(obj.df.columns)
        if missing:
            raise ValueError(f'{self.name}: missing required columns: ' + ', '.join(sorted(missing)))

        # check that some rows are left after the preprocessing
        if obj.df.empty:
            raise ValueError(f'{self.name}: no rows remain after preprocessing. The original classes split the dataset at 86,194 rows; use the full ODI.csv.')
        return obj

    def set_analysis(self, obj):
        """Store the loaded data and fill every tab with it."""
        self.analysis = obj
        self.filtered = obj.df.copy()

        # list of all player names for the drop-down in Player Explorer
        player_names = obj.df['Innings Player'].dropna().astype(str).unique().tolist()
        self.player_combo['values'] = sorted(player_names)

        self.refresh()
        self.show_records()
        self.draw_chart()

    def require_data(self):
        """Return True if a CSV is loaded, otherwise show a warning and return False."""
        if self.analysis is None:
            messagebox.showwarning('Dataset needed', 'Please open your ODI CSV file first.')
            return False
        return True

    # ---- actions ----
    def refresh(self):
        """Update the number cards and the small tables on the Dashboard."""
        if not self.require_data():
            return
        try:
            # compute_metrics() is written in BattingPage / BowlingPage
            metrics = self.compute_metrics()
            for key, value in metrics.items():
                self.metric_vars[key].set(value)

            # table_rows() is also written in BattingPage / BowlingPage
            all_rows = self.table_rows()
            for i in range(len(self.table_trees)):
                tree = self.table_trees[i]
                rows = all_rows[i]

                # clear the old rows, then add the new ones
                tree.delete(*tree.get_children())
                for row in rows:
                    values = []
                    for x in row:
                        values.append(fmt(x))
                    tree.insert('', 'end', values=values)
        except (ValueError, KeyError, TypeError) as exc:
            messagebox.showerror('Analysis error', str(exc))

    def draw_chart(self):
        """Draw the chart that is selected in the drop-down."""
        if not self.require_data():
            return

        title = self.chart_name.get()
        method, kind, axis_label = self.charts[title]
        try:
            # get the chart data by calling the analysis method by its name
            data = getattr(self.analysis, method)()

            self.figure.clear()
            ax = self.figure.add_subplot(111, facecolor=PANEL)

            if kind == 'line':
                # line chart (used for the year wise charts)
                ax.plot(data.index, data.values, color=ACCENT, marker='o', linewidth=2)
                ax.xaxis.set_major_locator(MaxNLocator(integer=True))   # show whole years only
                ax.set_xlabel('Year', color=MUTED)
                ax.set_ylabel(axis_label, color=MUTED)
                ax.grid(color='#2b4059', linestyle='--', linewidth=0.7)
            else:
                # horizontal bars, biggest value at the top
                # ([::-1] reverses the list so the biggest bar is drawn last, at the top)
                names = []
                for n in data.index:
                    names.append(str(n))
                names = names[::-1]
                values = list(data.values)[::-1]

                bars = ax.barh(names, values, color=ACCENT)

                # write the value at the end of every bar
                bar_labels = []
                for v in values:
                    bar_labels.append(fmt(v))
                ax.bar_label(bars, labels=bar_labels, padding=4, color=FG, fontsize=9)

                ax.margins(x=0.12)
                ax.set_xlabel(axis_label, color=MUTED)

            # styling that is the same for both chart types
            ax.set_title(title, color=FG, fontsize=13, fontweight='bold', pad=12)
            ax.tick_params(colors=FG)
            for spine in ax.spines.values():
                spine.set_color('#2b4059')

            self.figure.tight_layout()
            self.canvas.draw()
        except Exception as exc:
            messagebox.showerror('Chart error', f'{type(exc).__name__}: {exc}')

    def save_chart(self):
        """Save the chart on the screen as a PNG image."""
        if not self.require_data():
            return

        path = filedialog.asksaveasfilename(defaultextension='.png',
                                            filetypes=[('PNG image', '*.png')],
                                            initialfile=f'odi_{self.name.lower()}_chart.png')
        if not path:
            return      # the user closed the save window

        try:
            self.figure.savefig(path, facecolor=self.figure.get_facecolor())
            self.status.set('Saved: ' + path)
        except OSError as exc:
            messagebox.showerror('Save error', str(exc))

    def search_player(self):
        """Show the summary of the player typed in the Player Explorer box."""
        if not self.require_data():
            return

        name = self.player_name.get().strip()
        if not name:
            messagebox.showwarning('Missing name', 'Enter or select a player name.')
            return

        # player_summary() gives a dictionary, or the text "Player not found"
        result = self.analysis.player_summary(name)
        if isinstance(result, str):
            text = result
        else:
            lines = []
            for key, value in result.items():
                lines.append(f'{key}:  {value}')
            text = '\n\n'.join(lines)

        # the text box is read only, so unlock it, change the text, then lock it again
        self.player_output.configure(state='normal')
        self.player_output.delete('1.0', 'end')
        self.player_output.insert('1.0', text)
        self.player_output.configure(state='disabled')

        self.status.set(f'{self.name} lookup: {name}')

    def filter_records(self):
        """Keep only the records whose player name contains the typed text."""
        if not self.require_data():
            return

        term = self.filter_text.get().strip()
        if not term:
            messagebox.showwarning('Missing filter', 'Enter a player name or part of a name.')
            return

        df = self.analysis.df
        names = df['Innings Player'].astype(str)
        matches = names.str.contains(term, case=False, regex=False, na=False)   # case=False ignores capital letters
        self.filtered = df[matches].copy()
        self.show_records()

    def clear_filter(self):
        """Remove the filter and show all the records again."""
        if not self.require_data():
            return

        self.filter_text.set('')
        self.filtered = self.analysis.df.copy()
        self.show_records()

    def show_records(self):
        """Fill the Dataset Browser table (only the first 500 rows, so the app stays fast)."""
        self.record_tree.delete(*self.record_tree.get_children())
        df = self.filtered

        for index, row in df.head(500).iterrows():
            values = []
            for heading, column in self.record_cols:
                values.append(fmt(row.get(column)))
            self.record_tree.insert('', 'end', values=values)

        self.record_count.config(text=f'{len(df):,} matching rows (first 500 displayed for responsiveness).')

    def export_csv(self):
        """Save the records shown in the Dataset Browser as a CSV file."""
        if not self.require_data():
            return

        if self.filtered is None or self.filtered.empty:
            messagebox.showwarning('No records', 'No records to export.')
            return

        path = filedialog.asksaveasfilename(defaultextension='.csv',
                                            filetypes=[('CSV files', '*.csv')],
                                            initialfile=f'odi_{self.name.lower()}_records.csv')
        if not path:
            return      # the user closed the save window

        try:
            self.filtered.to_csv(path, index=False)
            self.status.set('Saved: ' + path)
            messagebox.showinfo('Export complete', f'Saved {len(self.filtered):,} records.')
        except OSError as exc:
            messagebox.showerror('Save error', str(exc))


# ---------------------------------------------------------------
# BattingPage : AnalysisPage filled in with batting details
# ---------------------------------------------------------------
class BattingPage(AnalysisPage):
    name = 'Batting'
    analysis_class = ODIAnalysis

    # titles of the number cards on the Dashboard
    metric_names = ['Innings Records', 'Average Strike Rate', 'Total Sixes', 'Total Fours', 'Highest Innings', 'Lowest Innings']
    cards_per_row = 3

    # small tables on the Dashboard: (title, column headings)
    tables = [('Top five scoring innings', ['Player', 'Runs']),
              ('Best batting averages (min 20 inns)', ['Player', 'Average'])]

    # charts: 'title shown in the drop-down': (method name in ODIAnalysis, chart type, axis label)
    charts = {'Top 10 career run scorers': ('top_career_runs', 'bar', 'Runs'),
              'Top 10 batting averages (min 20 innings)': ('top_batting_averages', 'bar', 'Batting average'),
              'Average runs per innings by year': ('runs_per_year', 'line', 'Average runs per innings'),
              'Total runs by country': ('runs_by_country', 'bar', 'Runs'),
              'Innings by score range': ('innings_by_score_range', 'bar', 'Number of innings')}

    # columns of the Dataset Browser: (heading shown, column name in the CSV)
    record_cols = [('Player', 'Innings Player'),
                   ('Runs', 'Innings Runs Scored Num'),
                   ('Balls', 'Innings Balls Faced'),
                   ('Fours', 'Innings Boundary Fours'),
                   ('Sixes', 'Innings Boundary Sixes'),
                   ('Strike Rate', 'Innings Batting Strike Rate'),
                   ('Opposition', 'Opposition'),
                   ('Date', 'Innings Date')]

    # columns that must be present in the CSV file
    required = {'Innings Player', 'Innings Runs Scored Num', 'Innings Boundary Sixes', 'Innings Boundary Fours', 'Innings Balls Faced', 'Innings Batting Strike Rate'}

    def compute_metrics(self):
        """Return the text for every number card on the batting Dashboard."""
        a = self.analysis
        df = a.df

        # rows of the highest and the lowest innings
        top = df.loc[df['Innings Runs Scored Num'].idxmax()]
        low = df.loc[df['Innings Runs Scored Num'].idxmin()]

        top_runs = top['Innings Runs Scored Num']
        top_player = top['Innings Player']
        low_runs = low['Innings Runs Scored Num']
        low_player = low['Innings Player']

        # {:,} adds commas (85,774) and {:.2f} keeps 2 decimals
        return {'Innings Records': f'{len(df):,}',
                'Average Strike Rate': f'{a.avg_strike_rate():.2f}',
                'Total Sixes': f'{a.total_six():,.0f}',
                'Total Fours': f'{a.total_fours():,.0f}',
                'Highest Innings': f"{top_runs:,.0f} — {top_player}",
                'Lowest Innings': f"{low_runs:,.0f} — {low_player}"}

    def table_rows(self):
        """Return the rows for the two small tables (same order as 'tables' above)."""
        top_innings = list(self.analysis.top_five_scorers_dict().items())
        top_averages = list(self.analysis.top_five_batting_average_dict().items())
        return [top_innings, top_averages]


# ---------------------------------------------------------------
# BowlingPage : AnalysisPage filled in with bowling details
# ---------------------------------------------------------------
class BowlingPage(AnalysisPage):
    name = 'Bowling'
    analysis_class = ODIBowlingAnalysis

    # titles of the number cards on the Dashboard
    metric_names = ['Bowling Innings', 'Total Wickets', 'Average Economy Rate', 'Total Maidens', '4 Wicket Hauls', '5 Wicket Hauls', 'Best Bowling', 'Most Expensive Spell']
    cards_per_row = 4

    # small tables on the Dashboard: (title, column headings)
    tables = [('Top five bowling innings', ['Player', 'Wickets']),
              ('Top five career wickets', ['Player', 'Wickets']),
              ('Best economy (min 100 overs)', ['Player', 'Economy'])]

    # charts: 'title shown in the drop-down': (method name in ODIBowlingAnalysis, chart type, axis label)
    charts = {'Top 10 career wicket takers': ('top_career_wickets', 'bar', 'Wickets'),
              'Top 10 best economy rates (min 100 overs)': ('best_economy_rates', 'bar', 'Economy rate (runs per over)'),
              'Average economy rate by year': ('economy_per_year', 'line', 'Average economy rate'),
              'Total wickets by country': ('wickets_by_country', 'bar', 'Wickets'),
              'Innings by wickets taken': ('innings_by_wicket_range', 'bar', 'Number of innings')}

    # columns of the Dataset Browser: (heading shown, column name in the CSV)
    record_cols = [('Player', 'Innings Player'),
                   ('Overs', 'Innings Overs Bowled'),
                   ('Maidens', 'Innings Maidens Bowled'),
                   ('Runs', 'Innings Runs Conceded'),
                   ('Wickets', 'Innings Wickets Taken'),
                   ('Economy', 'Innings Economy Rate'),
                   ('Opposition', 'Opposition'),
                   ('Date', 'Innings Date')]

    # columns that must be present in the data
    required = {'Innings Player', 'Innings Overs Bowled', 'Innings Maidens Bowled', 'Innings Runs Conceded', 'Innings Wickets Taken', 'Innings Economy Rate', 'Balls Bowled'}

    def compute_metrics(self):
        """Return the text for every number card on the bowling Dashboard."""
        a = self.analysis
        df = a.df

        # best bowling = most wickets, and for the same wickets the fewest runs
        sorted_df = df.sort_values(by=['Innings Wickets Taken', 'Innings Runs Conceded'], ascending=[False, True])
        best = sorted_df.iloc[0]

        # most expensive spell = most runs conceded
        costly = df.loc[df['Innings Runs Conceded'].idxmax()]

        best_wickets = best['Innings Wickets Taken']
        best_runs = best['Innings Runs Conceded']
        best_player = best['Innings Player']
        costly_runs = costly['Innings Runs Conceded']
        costly_player = costly['Innings Player']

        # {:,} adds commas (46,238) and {:.0f} shows no decimals
        return {'Bowling Innings': f'{len(df):,}',
                'Total Wickets': f'{a.total_wickets():,.0f}',
                'Average Economy Rate': f'{a.avg_economy_rate():.2f}',
                'Total Maidens': f'{a.total_maidens():,.0f}',
                '4 Wicket Hauls': f'{a.total_four_wickets():,}',
                '5 Wicket Hauls': f'{a.total_five_wickets():,}',
                'Best Bowling': f"{best_wickets:.0f}/{best_runs:.0f} — {best_player}",
                'Most Expensive Spell': f"{costly_runs:.0f} runs — {costly_player}"}

    def table_rows(self):
        """Return the rows for the three small tables (same order as 'tables' above)."""
        top_innings = list(self.analysis.top_five_wicket_takers_dict().items())
        top_career = list(self.analysis.top_five_career_wickets_dict().items())
        best_economy = list(self.analysis.top_five_best_economy_dict().items())
        return [top_innings, top_career, best_economy]


# ---------------------------------------------------------------
# ODIApp : the main window
# ---------------------------------------------------------------
class ODIApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # window settings
        self.title('ODI Cricket | Analytics')
        self.geometry('1180x800')
        self.minsize(950, 650)
        self.configure(bg=BG)

        # colours and sizes of the tables and drop-downs
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.style.configure('Treeview', background=PANEL, foreground=FG, fieldbackground=PANEL, rowheight=27, borderwidth=0)
        self.style.configure('Treeview.Heading', background='#2b4059', foreground=FG, font=('Segoe UI', 10, 'bold'))
        self.style.map('Treeview', background=[('selected', '#236c7c')])
        self.style.configure('TCombobox', padding=6)

        self.build()

    def build(self):
        """Create the top bar, the status bar and both pages (Batting and Bowling)."""
        # top bar with the title and buttons
        header = tk.Frame(self, bg=BG, padx=24, pady=18)
        header.pack(fill='x')
        label(header, 'ODI  /  CRICKET ANALYTICS', 22, bold=True).pack(side='left')

        # buttons are packed from the right, so the first one packed ends up at the far right
        button(header, 'Open CSV', self.open_csv).pack(side='right')

        self.bowling_btn = button(header, 'Bowling', lambda: self.show_page('Bowling'))
        self.bowling_btn.pack(side='right', padx=(0, 10))

        self.batting_btn = button(header, 'Batting', lambda: self.show_page('Batting'))
        self.batting_btn.pack(side='right', padx=(0, 6))

        # shows the path of the opened file
        self.file_label = label(self, 'Choose your ODI.csv file to begin', 10, MUTED)
        self.file_label.pack(anchor='w', padx=24)

        # status bar at the bottom of the window
        self.status = tk.StringVar(value='Ready. Open an ODI CSV file.')
        tk.Label(self, textvariable=self.status, bg='#1c2b40', fg=MUTED, anchor='w', padx=20, pady=9).pack(side='bottom', fill='x')

        # the container holds whichever page is selected (Batting or Bowling)
        container = tk.Frame(self, bg=BG)
        container.pack(fill='both', expand=True, padx=24, pady=16)

        self.pages = {'Batting': BattingPage(container, self.status),
                      'Bowling': BowlingPage(container, self.status)}

        # Batting is shown first
        self.show_page('Batting')

    def show_page(self, name):
        """Show the Batting or Bowling page and highlight its button."""
        # hide both pages, then show only the chosen one
        for page_name, page in self.pages.items():
            page.pack_forget()
        self.pages[name].pack(fill='both', expand=True)

        # the selected button is green, the other one is grey
        if name == 'Batting':
            self.batting_btn.config(bg=BTN)
        else:
            self.batting_btn.config(bg=BTN_OFF)

        if name == 'Bowling':
            self.bowling_btn.config(bg=BTN)
        else:
            self.bowling_btn.config(bg=BTN_OFF)

    def open_csv(self):
        """Ask for the CSV file and load it into both pages."""
        path = filedialog.askopenfilename(title='Select ODI CSV dataset', filetypes=[('CSV files', '*.csv'), ('All files', '*.*')])
        if not path:
            return      # the user closed the window without choosing a file

        self.status.set('Loading dataset, please wait...')
        self.update_idletasks()     # show the message right now
        try:
            # build both analyses first, so a bad file never leaves the app half loaded
            loaded = {}
            for name, page in self.pages.items():
                loaded[name] = page.load(path)

            # everything loaded fine, so now give the data to the pages
            for name, page in self.pages.items():
                page.set_analysis(loaded[name])

            self.file_label.config(text=path)

            batting_count = len(loaded['Batting'].df)
            bowling_count = len(loaded['Bowling'].df)
            self.status.set(f"Loaded {batting_count:,} batting innings and {bowling_count:,} bowling innings.")

        except (OSError, ValueError, KeyError, UnicodeError, pd.errors.ParserError) as exc:
            # expected problems: wrong file, missing columns, unreadable file
            self.status.set('Could not load the dataset.')
            messagebox.showerror('Cannot load dataset', str(exc))
        except Exception as exc:
            # anything else we did not expect
            self.status.set('Could not load the dataset.')
            messagebox.showerror('Unexpected dataset error', f'{type(exc).__name__}: {exc}')


# the app starts here (only when this file is run directly with: python gui.py)
if __name__ == '__main__':
    ODIApp().mainloop()
