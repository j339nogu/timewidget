import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from datetime import timedelta
import requests  # 祝日情報を取得するためのライブラリ

# デフォルトの時間割データ
DEFAULT_SCHEDULE = [
    ["月曜日", "1限", "分散処理システム", "08:30-10:00", "EL15"],
    ["月曜日", "2限", "PBL", "10:20-11:50", "711"],
    ["水曜日", "2限", "サイバーセキュリティ", "10:00-11:50", "EL45"],
    ["金曜日", "1限", "PBL2", "09:15-10:00", "711"],
    ["金曜日", "2限", "PBL2", "10:20-11:50", "711"],
]

# 不規則なスケジュールを管理するクラス
class IrregularScheduleManager:
    def __init__(self):
        self.irregular_schedules = {}  # {日付文字列: スケジュールリスト}
        self.special_events = {}       # {日付文字列: イベント名}
        self.holidays = {}             # {日付文字列: 祝日名}

    def add_irregular_schedule(self, date_str, schedules):
        self.irregular_schedules[date_str] = schedules

    def add_special_event(self, date_str, event_name):
        self.special_events[date_str] = event_name

    def add_holiday(self, date_str, holiday_name):
        self.holidays[date_str] = holiday_name

    def get_schedule(self, date):
        date_str = date.strftime('%Y-%m-%d')

        if date_str in self.holidays:
            holiday_name = self.holidays[date_str]
            return [[date.strftime('%A'), "終日", holiday_name, "終日", "祝日"]]

        if date_str in self.special_events:
            event_name = self.special_events[date_str]
            return [[date.strftime('%A'), "終日", event_name, "終日", "指定会場"]]
        
        if date_str in self.irregular_schedules:
            return [[date.strftime('%A')] + schedule for schedule in self.irregular_schedules[date_str]]
            
        return None

    def load_holidays(self):
        # 祝日情報を取得するAPI (例として日本の祝日APIを使用)
        try:
            response = requests.get("https://holidays-jp.github.io/api/v1/date.json")
            response.raise_for_status()  # HTTPエラーが発生した場合は例外を発生させる
            holidays_data = response.json()
            
            if not holidays_data:  # データが空の場合
                messagebox.showwarning("警告", "祝日情報が空です。")
                return
            
            for date_str, holiday_name in holidays_data.items():
                self.add_holiday(date_str, holiday_name)
                self.add_holiday(date_str, holiday_name)
        except requests.exceptions.RequestException as e:
            messagebox.showerror("エラー", f"祝日情報の取得に失敗しました: {e}")
        except ValueError as e:
            messagebox.showerror("エラー", f"無効なJSON形式です: {e}")



# ウィジェットウィンドウの作成
def create_widget_window():
    schedule = DEFAULT_SCHEDULE
    current_view = "daily"
    current_date = datetime.date.today()
    
    irregular_manager = IrregularScheduleManager()
    irregular_manager.load_holidays()  # 祝日情報をロード
    irregular_manager.add_special_event(
        (datetime.date.today() + timedelta(days=7)).strftime('%Y-%m-%d'),
        "全国模試"
    )
    irregular_manager.add_irregular_schedule(
        (datetime.date.today() + timedelta(days=3)).strftime('%Y-%m-%d'),
        [["1限", "特別講座", "9:00-12:00", "大講堂"],
         ["2限", "個別指導", "13:00-15:00", "図書室"]]
    )

    def get_schedule_for_date(date):
        irregular_schedule = irregular_manager.get_schedule(date)
        if irregular_schedule:
            return irregular_schedule
        
        weekday_jp = date.strftime('%A')
        weekday_map = {
            "Monday": "月曜日",
            "Tuesday": "火曜日",
            "Wednesday": "水曜日",
            "Thursday": "木曜日",
            "Friday": "金曜日",
            "Saturday": "土曜日",
            "Sunday": "日曜日",
        }
        target_day = weekday_map.get(weekday_jp, weekday_jp)
        daily_schedule = [s for s in schedule if s[0] == target_day]
        if not daily_schedule:
            return [["授業はありません。", "", "", "", ""]]
        return daily_schedule

    def refresh_view(view_type=None):
        nonlocal current_view
        if view_type is not None:
            current_view = view_type
        
        for row in tree.get_children():
            tree.delete(row)
            
        if current_view == "daily":
            daily_schedule = get_schedule_for_date(current_date)
            date_str = current_date.strftime('%Y年%m月%d日')
            header.config(text=f"時間割 - {date_str}({current_date.strftime('%A')})")
            nav_frame.pack(fill=tk.X, pady=2)
            for entry in daily_schedule:
                tree.insert("", "end", values=entry)
                
        elif current_view == "weekly":
            header.config(text=f"時間割 - 週間スケジュール")
            nav_frame.pack_forget()
            for entry in schedule:
                tree.insert("", "end", values=entry)

    def navigate_day(direction):
        nonlocal current_date
        if direction == "next":
            current_date += timedelta(days=1)
        else:
            current_date -= timedelta(days=1)
        refresh_view()

    def add_irregular_schedule():
        input_window = tk.Toplevel(root)
        input_window.title("イレギュラー授業の追加")

        tk.Label(input_window, text="日付 (YYYY-MM-DD):").grid(row=0, column=0)
        date_entry = tk.Entry(input_window)
        date_entry.grid(row=0, column=1)

        tk.Label(input_window, text="時限:").grid(row=1, column=0)
        period_entry = tk.Entry(input_window)
        period_entry.grid(row=1, column=1)

        tk.Label(input_window, text="科目:").grid(row=2, column=0)
        subject_entry = tk.Entry(input_window)
        subject_entry.grid(row=2, column=1)

        tk.Label(input_window, text="時間:").grid(row=3, column=0)
        time_entry = tk.Entry(input_window)
        time_entry.grid(row=3, column=1)

        tk.Label(input_window, text="教室:").grid(row=4, column=0)
        classroom_entry = tk.Entry(input_window)
        classroom_entry.grid(row=4, column=1)

        def submit():
            date_str = date_entry.get()
            period = period_entry.get()
            subject = subject_entry.get()
            time = time_entry.get()
            classroom = classroom_entry.get()

            if date_str and period and subject and time and classroom:
                irregular_manager.add_irregular_schedule(date_str, [[period, subject, time, classroom]])
                messagebox.showinfo("成功", "イレギュラー授業が追加されました。")
                input_window.destroy()
            else:
                messagebox.showwarning("警告", "すべてのフィールドを入力してください。")

        tk.Button(input_window, text="追加", command=submit).grid(row=5, columnspan=2)

    root = tk.Tk()
    root.title("時間割ウィジェット")
    root.geometry("500x300")
    root.overrideredirect(True)
    root.wm_attributes("-transparentcolor", "#ffffff")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    widget_width = 500
    widget_height = 300
    default_x = screen_width - widget_width - 10
    default_y = 10
    root.geometry(f"{widget_width}x{widget_height}+{default_x}+{default_y}")

    bg_frame = tk.Frame(root, bg="#ffffff")
    bg_frame.pack(fill=tk.BOTH, expand=True)

    header_frame = tk.Frame(bg_frame, bg="#4682B4")
    header_frame.pack(fill=tk.X)

    nav_frame = tk.Frame(header_frame, bg="#4682B4")
    nav_frame.pack(fill=tk.X, pady=2)

    btn_prev = tk.Button(nav_frame, text="←", command=lambda: navigate_day("prev"), font=("Arial", 14, "bold"), fg="white", bg="#5B9BD5")
    btn_prev.pack(side=tk.LEFT, padx=5)

    header = tk.Label(
        nav_frame,
        text="時間割ウィジェット",
        font=("Arial", 12, "bold"),
        bg="#4682B4",
        fg="white",
        pady=5,
    )
    header.pack(side=tk.LEFT, expand=True)

    btn_next = tk.Button(nav_frame, text="→", command=lambda: navigate_day("next"), font=("Arial", 14, "bold"), fg="white", bg="#5B9BD5")
    btn_next.pack(side=tk.RIGHT, padx=5)

    tree_frame = tk.Frame(bg_frame, bg="#ffffff")
    tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    scrollbar = ttk.Scrollbar(tree_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    columns = ("day", "period", "subject", "time", "classroom")
    tree = ttk.Treeview(
        tree_frame,
        columns=columns,
        show="headings",
        height=10,
        yscrollcommand=scrollbar.set,
    )
    tree.heading("day", text="曜日")
    tree.heading("period", text="時限")
    tree.heading("subject", text="科目")
    tree.heading("time", text="時間")
    tree.heading("classroom", text="教室")

    tree.column("day", anchor="center", width=80)
    tree.column("period", anchor="center", width=60)
    tree.column("subject", anchor="center", width=100)
    tree.column("time", anchor="center", width=120)
    tree.column("classroom", anchor="center", width=100)

    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar.config(command=tree.yview)

    button_frame = tk.Frame(bg_frame, bg="#ffffff")
    button_frame.pack(fill=tk.X, pady=0)

    btn_daily = tk.Button(
        button_frame,
        text="日別",
        command=lambda: refresh_view("daily"),
        font=("Arial", 12),
    )
    btn_daily.pack(side=tk.LEFT, padx=5)

    btn_weekly = tk.Button(
        button_frame,
        text="週別",
        command=lambda: refresh_view("weekly"),
        font=("Arial", 12),
    )
    btn_weekly.pack(side=tk.LEFT, padx=5)

    btn_add_irregular = tk.Button(
        button_frame,
        text="イレギュラー授業追加",
        command=add_irregular_schedule,
        font=("Arial", 12),
    )
    btn_add_irregular.pack(side=tk.LEFT, padx=5)

    btn_close = tk.Button(
        button_frame,
        text="閉じる",
        command=root.destroy,
        font=("Arial", 12),
        bg="red",
        fg="white"
    )
    btn_close.pack(side=tk.RIGHT, padx=5)

    # ドラッグ移動機能
    def start_drag(event):
        root.x = event.x
        root.y = event.y

    def drag(event):
        deltax = event.x - root.x
        deltay = event.y - root.y
        x = root.winfo_x() + deltax
        y = root.winfo_y() + deltay
        root.geometry(f"+{x}+{y}")

    root.bind("<Button-1>", start_drag)
    root.bind("<B1-Motion>", drag)

    refresh_view("daily")
    root.lower()  # 起動時に最背面に配置
    root.mainloop()

# アプリケーションの起動
create_widget_window()
