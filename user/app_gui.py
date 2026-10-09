import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import csv
import random
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

from core import (
    TOTAL_NUMBERS, DRAW_COUNT, DEFAULT_ZODIACS, DEFAULT_BET_TYPES,
    BetManager, get_zodiac_for_number, I18N
)

class Lucky48HostApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Lucky48 - 48选7 智能彩票与投注结算总控系统")
        self.root.geometry("1100x750")
        self.root.minsize(950, 650)

        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
        self.manager = BetManager(self.config_file)

        self.lang = "zh"
        self.self_bets: List[Dict[str, Any]] = []
        self.client_slips: Dict[str, Dict[str, Any]] = {}
        self.current_draw: Optional[List[int]] = None
        self.locked_numbers: Dict[int, int] = {}

        self.setup_styles()
        self.build_header()
        self.build_notebook()
        self.build_footer()
        self.refresh_all_views()

    def t(self, key: str) -> str:
        return I18N.get(self.lang, {}).get(key, key)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=[12, 6])
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))
        style.configure("Treeview", font=("Segoe UI", 9), rowheight=24)

    def build_header(self):
        header_frame = tk.Frame(self.root, bg="#0f172a", height=50)
        header_frame.pack(side=tk.TOP, fill=tk.X)

        title_label = tk.Label(
            header_frame, 
            text="★ Lucky48 庄家总控与投注结算平台",
            font=("Segoe UI", 14, "bold"),
            fg="#f8fafc",
            bg="#0f172a"
        )
        title_label.pack(side=tk.LEFT, padx=16, pady=10)
        self.header_title = title_label

        ctrl_frame = tk.Frame(header_frame, bg="#0f172a")
        ctrl_frame.pack(side=tk.RIGHT, padx=16)

        date_lbl = tk.Label(ctrl_frame, text="开奖日期:", fg="#94a3b8", bg="#0f172a", font=("Segoe UI", 9))
        date_lbl.pack(side=tk.LEFT, padx=4)
        self.header_date_lbl = date_lbl

        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        date_entry = tk.Entry(ctrl_frame, textvariable=self.date_var, width=12, font=("Segoe UI", 9))
        date_entry.pack(side=tk.LEFT, padx=4)

        self.lang_btn = tk.Button(
            ctrl_frame, 
            text="English", 
            command=self.toggle_language,
            bg="#334155", 
            fg="#ffffff", 
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=8
        )
        self.lang_btn.pack(side=tk.LEFT, padx=8)

    def build_notebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=4)

        self.tab_generator = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_generator, text="🎲 开奖生成与控盘")
        self.build_tab_generator()

        self.tab_combined = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_combined, text="📊 全盘汇总")
        self.build_tab_combined()

        self.tab_clients = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_clients, text="📥 客户注单管理")
        self.build_tab_clients()

        self.tab_self = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_self, text="✍️ 庄家录单")
        self.build_tab_self()

        self.tab_rules = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_rules, text="⚙️ 规则与生肖")
        self.build_tab_rules()

        self.tab_reports = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_reports, text="📑 报表对账")
        self.build_tab_reports()

    def build_tab_generator(self):
        pane = self.tab_generator

        stats_frame = tk.Frame(pane, bg="#1e293b", pady=8, padx=8)
        stats_frame.pack(fill=tk.X, padx=8, pady=6)

        self.stat_total_in = self.create_stat_widget(stats_frame, "总受注额 (Bet Pool)", "¥0.00")
        self.stat_target_out = self.create_stat_widget(stats_frame, "目标赔付额 (Target)", "¥0.00", color="#f59e0b")
        self.stat_actual_out = self.create_stat_widget(stats_frame, "实际赔付额 (Settled)", "--", color="#60a5fa")
        self.stat_house_net = self.create_stat_widget(stats_frame, "庄家盈亏 (House Net)", "--", color="#10b981")

        ball_frame = tk.LabelFrame(pane, text=" 7个开奖号码 (前6位正码 + 第7位特码Mn) ", font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        ball_frame.pack(fill=tk.X, padx=8, pady=6)

        hint_lbl = tk.Label(ball_frame, text="💡 提示: 可手工固定(锁定) 1 个或多个号码，控盘算法将自动维持手选号码并智能生成剩余号码", fg="#64748b", font=("Segoe UI", 9))
        hint_lbl.pack(anchor=tk.W, pady=(0, 6))

        slots_sub = tk.Frame(ball_frame)
        slots_sub.pack()

        self.ball_labels: List[tk.Label] = []
        self.ball_lock_vars: List[tk.StringVar] = []

        for i in range(7):
            is_mn = (i == 6)
            b_box = tk.Frame(slots_sub, padx=6)
            b_box.pack(side=tk.LEFT)

            slot_title = "★特码(Mn)" if is_mn else f"正码 {i+1}"
            t_lbl = tk.Label(b_box, text=slot_title, font=("Segoe UI", 8, "bold"), fg="#e11d48" if is_mn else "#1e3a8a")
            t_lbl.pack()

            bg_c = "#f43f5e" if is_mn else "#2563eb"
            b_lbl = tk.Label(b_box, text="?", font=("Segoe UI", 16, "bold"), width=4, height=2, bg=bg_c, fg="#ffffff", relief=tk.RAISED)
            b_lbl.pack(pady=2)
            self.ball_labels.append(b_lbl)

            l_var = tk.StringVar(value="")
            self.ball_lock_vars.append(l_var)
            lock_entry = tk.Entry(b_box, textvariable=l_var, width=5, justify='center', font=("Segoe UI", 9))
            lock_entry.pack(pady=2)

        btn_unlock = tk.Button(slots_sub, text="全部解锁", command=self.clear_all_locks, bg="#e2e8f0", font=("Segoe UI", 8))
        btn_unlock.pack(side=tk.LEFT, padx=10)

        slider_frame = tk.LabelFrame(pane, text=" 控盘目标赔付比例调节杆 (1-100% 档位) ", font=("Segoe UI", 10, "bold"), padx=12, pady=8)
        slider_frame.pack(fill=tk.X, padx=8, pady=6)

        slider_top = tk.Frame(slider_frame)
        slider_top.pack(fill=tk.X)

        s_desc = tk.Label(slider_top, text="滑动调节控盘赔付率 (1% 庄家最高利润 ➔ 30% 常规盈利 ➔ 100% 自然赔付):", font=("Segoe UI", 9), fg="#475569")
        s_desc.pack(side=tk.LEFT)

        self.slider_val_lbl = tk.Label(slider_top, text="30%", font=("Segoe UI", 13, "bold"), fg="#d97706")
        self.slider_val_lbl.pack(side=tk.RIGHT)

        self.payout_slider = tk.Scale(
            slider_frame, 
            from_=1, to=100, 
            orient=tk.HORIZONTAL, 
            showvalue=False,
            command=self.on_slider_change,
            relief=tk.FLAT
        )
        self.payout_slider.set(30)
        self.payout_slider.pack(fill=tk.X, pady=4)

        btn_box = tk.Frame(pane)
        btn_box.pack(fill=tk.X, padx=8, pady=8)

        self.btn_gen_optimized = tk.Button(
            btn_box, 
            text="⚡ 按控盘赔付率生成 7 个号码", 
            command=self.generate_optimized_draw,
            bg="#d97706", 
            fg="#ffffff", 
            font=("Segoe UI", 10, "bold"),
            padx=12, pady=6
        )
        self.btn_gen_optimized.pack(side=tk.LEFT, padx=4)

        self.btn_gen_fair = tk.Button(
            btn_box, 
            text="🎲 完全随机生成", 
            command=self.generate_fair_draw,
            bg="#475569", 
            fg="#ffffff", 
            font=("Segoe UI", 10),
            padx=10, pady=6
        )
        self.btn_gen_fair.pack(side=tk.LEFT, padx=4)

        self.btn_settle = tk.Button(
            btn_box, 
            text="✅ 一键全盘开奖结算", 
            command=self.settle_all_tabs,
            bg="#059669", 
            fg="#ffffff", 
            font=("Segoe UI", 10, "bold"),
            padx=14, pady=6
        )
        self.btn_settle.pack(side=tk.LEFT, padx=4)

        self.btn_reset_draw = tk.Button(
            btn_box, 
            text="重置开奖码", 
            command=self.reset_draw,
            bg="#dc2626", 
            fg="#ffffff", 
            font=("Segoe UI", 9),
            padx=10, pady=6
        )
        self.btn_reset_draw.pack(side=tk.RIGHT, padx=4)

        table_frame = tk.Frame(pane)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        columns = ("source", "count", "bet_amt", "payout", "client_net", "house_net", "win_rate")
        self.tree_overview = ttk.Treeview(table_frame, columns=columns, show="headings", height=6)
        self.tree_overview.heading("source", text="注单来源/客户")
        self.tree_overview.heading("count", text="注数")
        self.tree_overview.heading("bet_amt", text="下注总额")
        self.tree_overview.heading("payout", text="中奖赔付")
        self.tree_overview.heading("client_net", text="客户盈亏")
        self.tree_overview.heading("house_net", text="庄家盈亏")
        self.tree_overview.heading("win_rate", text="中奖率")

        self.tree_overview.column("source", width=160)
        self.tree_overview.column("count", width=60, anchor='center')
        self.tree_overview.column("bet_amt", width=100, anchor='e')
        self.tree_overview.column("payout", width=100, anchor='e')
        self.tree_overview.column("client_net", width=100, anchor='e')
        self.tree_overview.column("house_net", width=100, anchor='e')
        self.tree_overview.column("win_rate", width=80, anchor='center')

        self.tree_overview.pack(fill=tk.BOTH, expand=True)

    def create_stat_widget(self, parent, title, val, color="#ffffff"):
        box = tk.Frame(parent, bg="#0f172a", padx=12, pady=6, relief=tk.GROOVE, bd=1)
        box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)
        t_lbl = tk.Label(box, text=title, font=("Segoe UI", 8), fg="#94a3b8", bg="#0f172a")
        t_lbl.pack(anchor=tk.W)
        v_lbl = tk.Label(box, text=val, font=("Segoe UI", 13, "bold"), fg=color, bg="#0f172a")
        v_lbl.pack(anchor=tk.W)
        return v_lbl

    def on_slider_change(self, val):
        self.slider_val_lbl.config(text=f"{val}%")
        all_bets = self.get_all_combined_bets()
        total_in = sum(float(b.get("bet_amount", 0.0)) for b in all_bets)
        target_amt = (float(val) / 100.0) * total_in
        self.stat_target_out.config(text=f"¥{target_amt:.2f}")

    def clear_all_locks(self):
        for v in self.ball_lock_vars:
            v.set("")

    def get_locks_from_ui(self) -> Dict[int, int]:
        locks = {}
        for i, v in enumerate(self.ball_lock_vars):
            txt = v.get().strip()
            if txt.isdigit():
                num = int(txt)
                if 1 <= num <= 48:
                    locks[i] = num
        return locks

    def generate_optimized_draw(self):
        locks = self.get_locks_from_ui()
        slider_val = float(self.payout_slider.get())
        all_bets = self.get_all_combined_bets()

        draw, stats = self.manager.generate_draw_numbers(
            locked_numbers=locks,
            target_payout_pct=slider_val,
            all_bets=all_bets,
            candidate_samples=2500
        )
        self.current_draw = draw
        self.update_ball_labels()
        self.settle_all_tabs()

        total_in = sum(float(b.get("bet_amount", 0.0)) for b in all_bets)
        actual_p = stats["total_payout"] if stats else 0.0
        pct = (actual_p / total_in * 100) if total_in > 0 else 0.0

        messagebox.showinfo(
            "开奖生成成功",
            f"已成功控盘生成 7 个号码！\n"
            f"正码: {draw[:6]}\n特码(Mn): {draw[6]}\n"
            f"目标赔付率: {slider_val}%\n实际开奖赔付率: {pct:.1f}% (¥{actual_p:.2f})"
        )

    def generate_fair_draw(self):
        locks = self.get_locks_from_ui()
        draw, _ = self.manager.generate_draw_numbers(locked_numbers=locks)
        self.current_draw = draw
        self.update_ball_labels()
        self.settle_all_tabs()
        messagebox.showinfo("完全随机开奖", f"开奖号码: {draw[:6]} + 特码[{draw[6]}]")

    def reset_draw(self):
        self.current_draw = None
        for lbl in self.ball_labels:
            lbl.config(text="?")
        self.settle_all_tabs()

    def update_ball_labels(self):
        if not self.current_draw:
            return
        for i in range(7):
            self.ball_labels[i].config(text=str(self.current_draw[i]))

    def build_tab_combined(self):
        pane = self.tab_combined

        top_bar = tk.Frame(pane)
        top_bar.pack(fill=tk.X, padx=8, pady=6)

        btn_csv = tk.Button(top_bar, text="📄 导出汇总 CSV", command=self.export_combined_csv, bg="#334155", fg="#fff")
        btn_csv.pack(side=tk.LEFT, padx=4)

        btn_json = tk.Button(top_bar, text="💾 导出汇总 JSON", command=self.export_combined_json, bg="#334155", fg="#fff")
        btn_json.pack(side=tk.LEFT, padx=4)

        cols = ("idx", "client", "device", "type", "selection", "amount", "ratio", "possible", "settled", "net")
        self.tree_master = ttk.Treeview(pane, columns=cols, show="headings")
        self.tree_master.heading("idx", text="#")
        self.tree_master.heading("client", text="客户姓名")
        self.tree_master.heading("device", text="设备ID")
        self.tree_master.heading("type", text="玩法")
        self.tree_master.heading("selection", text="投注内容")
        self.tree_master.heading("amount", text="金额")
        self.tree_master.heading("ratio", text="赔率")
        self.tree_master.heading("possible", text="最高奖金")
        self.tree_master.heading("settled", text="结果")
        self.tree_master.heading("net", text="盈亏")

        self.tree_master.column("idx", width=40, anchor='center')
        self.tree_master.column("client", width=90)
        self.tree_master.column("device", width=90)
        self.tree_master.column("type", width=70, anchor='center')
        self.tree_master.column("selection", width=120)
        self.tree_master.column("amount", width=70, anchor='e')
        self.tree_master.column("ratio", width=60, anchor='center')
        self.tree_master.column("possible", width=80, anchor='e')
        self.tree_master.column("settled", width=80, anchor='center')
        self.tree_master.column("net", width=80, anchor='e')

        self.tree_master.tag_configure("win", foreground="#059669")
        self.tree_master.tag_configure("lose", foreground="#dc2626")

        scroll = ttk.Scrollbar(pane, orient=tk.VERTICAL, command=self.tree_master.yview)
        self.tree_master.configure(yscrollcommand=scroll.set)

        self.tree_master.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0), pady=6)
        scroll.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 8), pady=6)

    def build_tab_clients(self):
        pane = self.tab_clients

        top_bar = tk.Frame(pane)
        top_bar.pack(fill=tk.X, padx=8, pady=6)

        btn_import = tk.Button(top_bar, text="📂 导入客户注单文件 (JSON/CSV)", command=self.import_client_files, bg="#2563eb", fg="#fff", font=("Segoe UI", 9, "bold"))
        btn_import.pack(side=tk.LEFT, padx=4)

        btn_clear = tk.Button(top_bar, text="清空所有导入客户", command=self.clear_all_clients, bg="#dc2626", fg="#fff")
        btn_clear.pack(side=tk.RIGHT, padx=4)

        middle_pane = tk.PanedWindow(pane, orient=tk.HORIZONTAL)
        middle_pane.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        left_frame = tk.Frame(middle_pane, width=220)
        middle_pane.add(left_frame, minsize=180)

        c_lbl = tk.Label(left_frame, text="客户文件列表 (点击切换):", font=("Segoe UI", 9, "bold"))
        c_lbl.pack(anchor=tk.W, pady=2)

        self.client_listbox = tk.Listbox(left_frame, font=("Segoe UI", 9))
        self.client_listbox.pack(fill=tk.BOTH, expand=True)
        self.client_listbox.bind('<<ListboxSelect>>', self.on_client_select)

        right_frame = tk.Frame(middle_pane)
        middle_pane.add(right_frame, minsize=400)

        self.client_info_lbl = tk.Label(right_frame, text="未选中任何客户", font=("Segoe UI", 10, "bold"), fg="#1e3a8a")
        self.client_info_lbl.pack(anchor=tk.W, pady=2)

        cols = ("line", "type", "selection", "amount", "ratio", "status", "net")
        self.tree_client_bets = ttk.Treeview(right_frame, columns=cols, show="headings")
        self.tree_client_bets.heading("line", text="行号")
        self.tree_client_bets.heading("type", text="玩法")
        self.tree_client_bets.heading("selection", text="投注内容")
        self.tree_client_bets.heading("amount", text="金额")
        self.tree_client_bets.heading("ratio", text="赔率")
        self.tree_client_bets.heading("status", text="状态")
        self.tree_client_bets.heading("net", text="盈亏")

        self.tree_client_bets.column("line", width=40, anchor='center')
        self.tree_client_bets.column("type", width=70, anchor='center')
        self.tree_client_bets.column("selection", width=120)
        self.tree_client_bets.column("amount", width=70, anchor='e')
        self.tree_client_bets.column("ratio", width=60, anchor='center')
        self.tree_client_bets.column("status", width=70, anchor='center')
        self.tree_client_bets.column("net", width=80, anchor='e')

        self.tree_client_bets.tag_configure("win", foreground="#059669")
        self.tree_client_bets.tag_configure("lose", foreground="#dc2626")

        self.tree_client_bets.pack(fill=tk.BOTH, expand=True)

    def import_client_files(self):
        filepaths = filedialog.askopenfilenames(
            title="选择客户导出的注单文件",
            filetypes=[("JSON & CSV 注单文件", "*.json;*.csv"), ("JSON Files", "*.json"), ("CSV Files", "*.csv")]
        )
        if not filepaths:
            return

        imported_count = 0
        for fp in filepaths:
            try:
                fname = os.path.basename(fp)
                if fp.endswith(".json"):
                    with open(fp, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        c_name = data.get("client_name", fname.replace(".json", ""))
                        d_id = data.get("device_id", "DEV-JSON")
                        bets = data.get("bets", [])
                        key = f"{c_name}_{d_id}"
                        self.client_slips[key] = {
                            "client_name": c_name,
                            "device_id": d_id,
                            "bets": bets
                        }
                        imported_count += 1
                elif fp.endswith(".csv"):
                    with open(fp, 'r', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        rows = list(reader)
                        if len(rows) > 1:
                            bets = []
                            c_name = fname.replace(".csv", "")
                            d_id = "DEV-CSV"
                            for r in rows[1:]:
                                if len(r) >= 7:
                                    c_name = r[1] or c_name
                                    d_id = r[3] or d_id
                                    b_type = r[4]
                                    sel = r[5]
                                    if ";" in sel:
                                        sel = [int(x) for x in sel.split(";") if x.isdigit()]
                                    elif sel.isdigit():
                                        sel = int(sel)
                                    b_amt = float(r[6])
                                    ratio = float(r[7]) if len(r) > 7 else self.manager.bet_types.get(b_type, {}).get("pay_ratio", 1.0)
                                    bets.append({
                                        "line": len(bets) + 1,
                                        "client": c_name,
                                        "device_id": d_id,
                                        "bet_type": b_type,
                                        "selection": sel,
                                        "bet_amount": b_amt,
                                        "pay_ratio": ratio,
                                        "possible_payout": b_amt * ratio
                                    })
                            key = f"{c_name}_{d_id}"
                            self.client_slips[key] = {
                                "client_name": c_name,
                                "device_id": d_id,
                                "bets": bets
                            }
                            imported_count += 1
            except Exception as e:
                print(f"Error loading {fp}: {e}")

        self.update_client_listbox()
        self.settle_all_tabs()
        messagebox.showinfo("导入完成", f"已成功导入/更新 {imported_count} 个客户文件！")

    def update_client_listbox(self):
        self.client_listbox.delete(0, tk.END)
        for k, v in self.client_slips.items():
            self.client_listbox.insert(tk.END, f"{v['client_name']} ({len(v['bets'])}注)")

    def on_client_select(self, event):
        sel_idx = self.client_listbox.curselection()
        if not sel_idx:
            return
        keys = list(self.client_slips.keys())
        key = keys[sel_idx[0]]
        client_data = self.client_slips[key]

        self.client_info_lbl.config(
            text=f"客户: {client_data['client_name']} | 设备: {client_data['device_id']} | 注数: {len(client_data['bets'])}"
        )

        for row in self.tree_client_bets.get_children():
            self.tree_client_bets.delete(row)

        for b in client_data['bets']:
            sel_str = str(b.get("selection"))
            status_str = "待开奖"
            net_str = "--"
            tag = ""
            if b.get("settled"):
                if b.get("won"):
                    status_str = "中奖"
                    net_str = f"+¥{b.get('net_profit', 0):.2f}"
                    tag = "win"
                else:
                    status_str = "未中"
                    net_str = f"-¥{abs(b.get('net_profit', 0)):.2f}"
                    tag = "lose"

            self.tree_client_bets.insert(
                "", tk.END,
                values=(
                    b.get("line", ""),
                    b.get("bet_type", ""),
                    sel_str,
                    f"¥{float(b.get('bet_amount', 0)):.2f}",
                    f"1:{b.get('pay_ratio', 1)}",
                    status_str,
                    net_str
                ),
                tags=(tag,)
            )

    def clear_all_clients(self):
        if messagebox.askyesno("清空确认", "确定清空所有导入的客户数据吗？"):
            self.client_slips.clear()
            self.update_client_listbox()
            for row in self.tree_client_bets.get_children():
                self.tree_client_bets.delete(row)
            self.settle_all_tabs()

    def build_tab_self(self):
        pane = self.tab_self

        in_box = tk.LabelFrame(pane, text=" 录入新注单 ", font=("Segoe UI", 9, "bold"), padx=10, pady=8)
        in_box.pack(fill=tk.X, padx=8, pady=6)

        row1 = tk.Frame(in_box)
        row1.pack(fill=tk.X, pady=4)

        tk.Label(row1, text="客户姓名:").pack(side=tk.LEFT)
        self.self_client_entry = tk.Entry(row1, width=12)
        self.self_client_entry.insert(0, "现场客户")
        self.self_client_entry.pack(side=tk.LEFT, padx=6)

        tk.Label(row1, text="玩法:").pack(side=tk.LEFT, padx=(10, 0))
        self.self_type_cb = ttk.Combobox(row1, values=list(self.manager.bet_types.keys()), width=10, state="readonly")
        self.self_type_cb.set("TM")
        self.self_type_cb.pack(side=tk.LEFT, padx=6)
        self.self_type_cb.bind("<<ComboboxSelected>>", self.on_self_type_change)

        tk.Label(row1, text="投注金额:").pack(side=tk.LEFT, padx=(10, 0))
        self.self_amt_entry = tk.Entry(row1, width=8)
        self.self_amt_entry.insert(0, "10")
        self.self_amt_entry.pack(side=tk.LEFT, padx=6)

        tk.Label(row1, text="投注内容(号码/生肖/单双):").pack(side=tk.LEFT, padx=(10, 0))
        self.self_pick_entry = tk.Entry(row1, width=16)
        self.self_pick_entry.pack(side=tk.LEFT, padx=6)

        btn_add = tk.Button(row1, text="➕ 添加该注", command=self.add_self_bet, bg="#2563eb", fg="#fff", font=("Segoe UI", 9, "bold"))
        btn_add.pack(side=tk.LEFT, padx=10)

        self.self_hint_lbl = tk.Label(in_box, text="提示: TM 为特码 (输入 1-48 单个号码，例如 37)", fg="#64748b", font=("Segoe UI", 8))
        self.self_hint_lbl.pack(anchor=tk.W, pady=2)

        cols = ("line", "client", "type", "selection", "amount", "ratio", "possible", "status", "net")
        self.tree_self = ttk.Treeview(pane, columns=cols, show="headings")
        self.tree_self.heading("line", text="行号")
        self.tree_self.heading("client", text="客户")
        self.tree_self.heading("type", text="玩法")
        self.tree_self.heading("selection", text="投注内容")
        self.tree_self.heading("amount", text="金额")
        self.tree_self.heading("ratio", text="赔率")
        self.tree_self.heading("possible", text="最高奖金")
        self.tree_self.heading("status", text="开奖状态")
        self.tree_self.heading("net", text="盈亏")

        self.tree_self.column("line", width=40, anchor='center')
        self.tree_self.column("client", width=80)
        self.tree_self.column("type", width=70, anchor='center')
        self.tree_self.column("selection", width=120)
        self.tree_self.column("amount", width=70, anchor='e')
        self.tree_self.column("ratio", width=60, anchor='center')
        self.tree_self.column("possible", width=80, anchor='e')
        self.tree_self.column("status", width=70, anchor='center')
        self.tree_self.column("net", width=80, anchor='e')

        self.tree_self.tag_configure("win", foreground="#059669")
        self.tree_self.tag_configure("lose", foreground="#dc2626")

        self.tree_self.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        b_box = tk.Frame(pane)
        b_box.pack(fill=tk.X, padx=8, pady=4)
        tk.Button(b_box, text="清空现场录单", command=self.clear_self_bets, bg="#ef4444", fg="#fff").pack(side=tk.RIGHT)

    def on_self_type_change(self, event):
        b_type = self.self_type_cb.get()
        info = self.manager.bet_types.get(b_type, {})
        self.self_hint_lbl.config(text=f"说明: {info.get('desc_zh', '')} | 赔率 1:{info.get('pay_ratio', 1)}")

    def add_self_bet(self):
        b_type = self.self_type_cb.get()
        pick_str = self.self_pick_entry.get().strip()
        amt_str = self.self_amt_entry.get().strip()
        client = self.self_client_entry.get().strip() or "现场客户"

        if not pick_str:
            messagebox.showwarning("提示", "请输入投注内容！")
            return
        try:
            amt = float(amt_str)
            if amt <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("提示", "请输入有效的投注金额！")
            return

        sel: Any = pick_str
        if "," in pick_str or " " in pick_str:
            parts = [x for x in pick_str.replace(",", " ").split() if x]
            if all(x.isdigit() for x in parts):
                sel = [int(x) for x in parts]
        elif pick_str.isdigit():
            sel = int(pick_str)

        rule = self.manager.bet_types.get(b_type, {})
        ratio = rule.get("pay_ratio", 1.0)

        bet = {
            "line": len(self.self_bets) + 1,
            "client": client,
            "device_id": "HOST-LOCAL",
            "bet_type": b_type,
            "category": rule.get("category", ""),
            "selection": sel,
            "bet_amount": amt,
            "pay_ratio": ratio,
            "possible_payout": amt * ratio,
            "timestamp": datetime.now().isoformat()
        }
        self.self_bets.append(bet)
        self.self_pick_entry.delete(0, tk.END)

        self.settle_all_tabs()

    def clear_self_bets(self):
        if messagebox.askyesno("清空确认", "确定清空所有自投录单吗？"):
            self.self_bets.clear()
            self.settle_all_tabs()

    def build_tab_rules(self):
        pane = self.tab_rules

        paned = tk.PanedWindow(pane, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        left = tk.Frame(paned)
        paned.add(left, minsize=450)

        tk.Label(left, text="玩法规则与赔率配置 (双击单元格修改):", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=4)

        cols = ("id", "name_zh", "name_en", "ratio", "prob")
        self.tree_rules = ttk.Treeview(left, columns=cols, show="headings", height=12)
        self.tree_rules.heading("id", text="代码")
        self.tree_rules.heading("name_zh", text="中文名")
        self.tree_rules.heading("name_en", text="英文名")
        self.tree_rules.heading("ratio", text="赔率 (1:X)")
        self.tree_rules.heading("prob", text="预设胜率%")

        self.tree_rules.column("id", width=60, anchor='center')
        self.tree_rules.column("name_zh", width=100)
        self.tree_rules.column("name_en", width=110)
        self.tree_rules.column("ratio", width=80, anchor='e')
        self.tree_rules.column("prob", width=80, anchor='center')

        self.tree_rules.pack(fill=tk.BOTH, expand=True)

        right = tk.Frame(paned)
        paned.add(right, minsize=400)

        tk.Label(right, text="12生肖名称与对应4个号码 (48码):", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=4)

        z_cols = ("z_id", "zh", "en", "nums")
        self.tree_zodiacs = ttk.Treeview(right, columns=z_cols, show="headings", height=12)
        self.tree_zodiacs.heading("z_id", text="生肖ID")
        self.tree_zodiacs.heading("zh", text="中文名")
        self.tree_zodiacs.heading("en", text="英文名")
        self.tree_zodiacs.heading("nums", text="包含号码")

        self.tree_zodiacs.column("z_id", width=60, anchor='center')
        self.tree_zodiacs.column("zh", width=90)
        self.tree_zodiacs.column("en", width=90)
        self.tree_zodiacs.column("nums", width=140)

        self.tree_zodiacs.pack(fill=tk.BOTH, expand=True)

        self.refresh_rules_and_zodiacs_tables()

    def refresh_rules_and_zodiacs_tables(self):
        for row in self.tree_rules.get_children():
            self.tree_rules.delete(row)
        for k, v in self.manager.bet_types.items():
            self.tree_rules.insert(
                "", tk.END,
                values=(v.get("id"), v.get("name_zh"), v.get("name_en"), v.get("pay_ratio"), f"{v.get('target_prob', 50)}%")
            )

        for row in self.tree_zodiacs.get_children():
            self.tree_zodiacs.delete(row)
        for z_id in range(1, 13):
            z = self.manager.zodiacs.get(z_id, {})
            self.tree_zodiacs.insert(
                "", tk.END,
                values=(f"Z{z_id}", z.get("name_zh"), z.get("name_en"), str(z.get("numbers")))
            )

    def build_tab_reports(self):
        pane = self.tab_reports

        box = tk.LabelFrame(pane, text=" 今日结算总览与报表导出 ", font=("Segoe UI", 10, "bold"), padx=16, pady=16)
        box.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        self.report_summary_txt = tk.Text(box, font=("Consolas", 10), height=14)
        self.report_summary_txt.pack(fill=tk.BOTH, expand=True, pady=8)

        btn_row = tk.Frame(box)
        btn_row.pack(fill=tk.X, pady=8)

        tk.Button(btn_row, text="📄 导出完整对账表 (CSV)", command=self.export_combined_csv, bg="#059669", fg="#fff", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_row, text="💾 导出完整备份 (JSON)", command=self.export_combined_json, bg="#2563eb", fg="#fff", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=4)

    def get_all_combined_bets(self) -> List[Dict[str, Any]]:
        all_bets = list(self.self_bets)
        for slip in self.client_slips.values():
            all_bets.extend(slip.get("bets", []))
        return all_bets

    def settle_all_tabs(self):
        all_bets = self.get_all_combined_bets()
        if self.current_draw:
            settled_bets, summary = self.manager.settle_all_bets(all_bets, self.current_draw)
            for b in self.self_bets:
                self.manager.settle_bet(b, self.current_draw)
            for slip in self.client_slips.values():
                for b in slip.get("bets", []):
                    self.manager.settle_bet(b, self.current_draw)
        else:
            for b in all_bets:
                b.pop("settled", None)
                b.pop("won", None)
                b.pop("payout", None)
                b.pop("net_profit", None)

        self.refresh_all_views()

    def refresh_all_views(self):
        all_bets = self.get_all_combined_bets()
        total_count = len(all_bets)
        total_in = sum(float(b.get("bet_amount", 0.0)) for b in all_bets)
        total_possible = sum(float(b.get("possible_payout", 0.0)) for b in all_bets)

        total_actual_payout = 0.0
        total_house_net = 0.0
        won_count = 0

        for b in all_bets:
            if b.get("settled"):
                p = float(b.get("payout", 0.0))
                net = float(b.get("net_profit", 0.0))
                total_actual_payout += p
                total_house_net -= net
                if b.get("won"):
                    won_count += 1

        self.stat_total_in.config(text=f"¥{total_in:.2f}")
        slider_val = float(self.payout_slider.get())
        target_amt = (slider_val / 100.0) * total_in
        self.stat_target_out.config(text=f"¥{target_amt:.2f}")

        if self.current_draw:
            self.stat_actual_out.config(text=f"¥{total_actual_payout:.2f}")
            self.stat_house_net.config(
                text=f"{'+' if total_house_net >= 0 else ''}¥{total_house_net:.2f}",
                fg="#10b981" if total_house_net >= 0 else "#dc2626"
            )
        else:
            self.stat_actual_out.config(text="--")
            self.stat_house_net.config(text="--", fg="#94a3b8")

        for r in self.tree_overview.get_children():
            self.tree_overview.delete(r)

        sources = []
        if self.self_bets:
            sources.append(("庄家现场录单 (Self)", self.self_bets))
        for k, v in self.client_slips.items():
            sources.append((v["client_name"], v["bets"]))

        for name, bets in sources:
            b_amt = sum(float(b.get("bet_amount", 0.0)) for b in bets)
            p_amt = sum(float(b.get("payout", 0.0)) for b in bets if b.get("settled"))
            c_net = sum(float(b.get("net_profit", 0.0)) for b in bets if b.get("settled"))
            h_net = -c_net
            w_cnt = sum(1 for b in bets if b.get("won"))
            w_rate = f"{(w_cnt / len(bets) * 100):.0f}%" if bets else "0%"

            self.tree_overview.insert(
                "", tk.END,
                values=(
                    name,
                    len(bets),
                    f"¥{b_amt:.2f}",
                    f"¥{p_amt:.2f}" if self.current_draw else "--",
                    f"{'+' if c_net >= 0 else ''}¥{c_net:.2f}" if self.current_draw else "--",
                    f"{'+' if h_net >= 0 else ''}¥{h_net:.2f}" if self.current_draw else "--",
                    w_rate if self.current_draw else "--"
                )
            )

        for r in self.tree_master.get_children():
            self.tree_master.delete(r)

        for idx, b in enumerate(all_bets, 1):
            status = "待开奖"
            net_str = "--"
            tag = ""
            if b.get("settled"):
                if b.get("won"):
                    status = "中奖"
                    net_str = f"+¥{b.get('net_profit', 0):.2f}"
                    tag = "win"
                else:
                    status = "未中"
                    net_str = f"-¥{abs(b.get('net_profit', 0)):.2f}"
                    tag = "lose"

            self.tree_master.insert(
                "", tk.END,
                values=(
                    idx,
                    b.get("client", "现场"),
                    b.get("device_id", "--"),
                    b.get("bet_type", ""),
                    str(b.get("selection")),
                    f"¥{float(b.get('bet_amount', 0)):.2f}",
                    f"1:{b.get('pay_ratio', 1)}",
                    f"¥{float(b.get('possible_payout', 0)):.2f}",
                    status,
                    net_str
                ),
                tags=(tag,)
            )

        for r in self.tree_self.get_children():
            self.tree_self.delete(r)
        for b in self.self_bets:
            status = "待开奖"
            net_str = "--"
            tag = ""
            if b.get("settled"):
                if b.get("won"):
                    status = "中奖"
                    net_str = f"+¥{b.get('net_profit', 0):.2f}"
                    tag = "win"
                else:
                    status = "未中"
                    net_str = f"-¥{abs(b.get('net_profit', 0)):.2f}"
                    tag = "lose"
            self.tree_self.insert(
                "", tk.END,
                values=(
                    b.get("line"),
                    b.get("client"),
                    b.get("bet_type"),
                    str(b.get("selection")),
                    f"¥{float(b.get('bet_amount', 0)):.2f}",
                    f"1:{b.get('pay_ratio', 1)}",
                    f"¥{float(b.get('possible_payout', 0)):.2f}",
                    status,
                    net_str
                ),
                tags=(tag,)
            )

        self.footer_lbl.config(
            text=f"总注数: {total_count} | 投注总额: ¥{total_in:.2f} | 最高可能赔付: ¥{total_possible:.2f} | 开奖实际赔付: {'¥' + f'{total_actual_payout:.2f}' if self.current_draw else '--'} | 庄家净盈亏: {'¥' + f'{total_house_net:.2f}' if self.current_draw else '--'}"
        )

        self.report_summary_txt.delete("1.0", tk.END)
        report_lines = [
            "=" * 60,
            f"          LUCKY48 彩票结算总对账单 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})",
            "=" * 60,
            f" 开奖号码: {self.current_draw if self.current_draw else '尚未开奖'}",
            f" 总客户/来源数: {len(sources)}",
            f" 全盘总注数: {total_count} 注",
            f" 受注资金总池: ¥{total_in:.2f}",
            f" 预估最高赔付: ¥{total_possible:.2f}",
            f" 实际中奖赔付: ¥{total_actual_payout:.2f} (赔付率: {(total_actual_payout / (total_in or 1) * 100):.1f}%)",
            f" 庄家净利盈亏: ¥{total_house_net:.2f}",
            "-" * 60,
            " 各客户结算明细汇总:",
        ]
        for name, bets in sources:
            b_amt = sum(float(b.get("bet_amount", 0.0)) for b in bets)
            p_amt = sum(float(b.get("payout", 0.0)) for b in bets if b.get("settled"))
            c_net = sum(float(b.get("net_profit", 0.0)) for b in bets if b.get("settled"))
            report_lines.append(f" - {name:<16} | 注数: {len(bets):<4} | 投注: ¥{b_amt:<8.2f} | 赔付: ¥{p_amt:<8.2f} | 客户净盈亏: ¥{c_net:<8.2f}")
        report_lines.append("=" * 60)
        self.report_summary_txt.insert(tk.END, "\n".join(report_lines))

    def build_footer(self):
        footer_frame = tk.Frame(self.root, bg="#0b0f19", height=30)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.footer_lbl = tk.Label(
            footer_frame, 
            text="总注数: 0 | 投注总额: ¥0.00 | 最高可能赔付: ¥0.00 | 开奖实际赔付: -- | 庄家净盈亏: --",
            font=("Segoe UI", 9),
            fg="#94a3b8",
            bg="#0b0f19"
        )
        self.footer_lbl.pack(side=tk.LEFT, padx=12, pady=4)

    def export_combined_csv(self):
        all_bets = self.get_all_combined_bets()
        if not all_bets:
            messagebox.showwarning("提示", "暂无注单可导出！")
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile=f"lucky48_combined_{datetime.now().strftime('%Y%m%d')}.csv"
        )
        if not filepath:
            return
        with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Line", "Client", "DeviceID", "Timestamp", "BetType", "Selection", "BetAmount", "PayRatio", "PossiblePayout", "Settled", "Won", "Payout", "NetProfit"])
            for idx, b in enumerate(all_bets, 1):
                writer.writerow([
                    idx,
                    b.get("client"),
                    b.get("device_id"),
                    b.get("timestamp"),
                    b.get("bet_type"),
                    b.get("selection"),
                    b.get("bet_amount"),
                    b.get("pay_ratio"),
                    b.get("possible_payout"),
                    b.get("settled", False),
                    b.get("won", False),
                    b.get("payout", 0.0),
                    b.get("net_profit", 0.0)
                ])
        messagebox.showinfo("导出成功", f"全盘汇总 CSV 已保存至:\n{filepath}")

    def export_combined_json(self):
        all_bets = self.get_all_combined_bets()
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")],
            initialfile=f"lucky48_combined_{datetime.now().strftime('%Y%m%d')}.json"
        )
        if not filepath:
            return
        data = {
            "app": "Lucky48_Host",
            "export_time": datetime.now().isoformat(),
            "draw_numbers": self.current_draw,
            "all_bets": all_bets
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("导出成功", f"全盘汇总 JSON 已保存至:\n{filepath}")

    def toggle_language(self):
        self.lang = "en" if self.lang == "zh" else "zh"
        self.lang_btn.config(text="中文" if self.lang == "en" else "English")
        if self.lang == "en":
            self.header_title.config(text="★ Lucky48 - Host Settlement & Payout Engine")
            self.header_date_lbl.config(text="Draw Date:")
            self.notebook.tab(0, text="🎲 Draw Generator & Control")
            self.notebook.tab(1, text="📊 Combined All Bets")
            self.notebook.tab(2, text="📥 Client Slips")
            self.notebook.tab(3, text="✍️ Host Self Input")
            self.notebook.tab(4, text="⚙️ Rules & Zodiacs")
            self.notebook.tab(5, text="📑 Reports")
            self.btn_gen_optimized.config(text="⚡ Auto Draw by Payout %")
            self.btn_gen_fair.config(text="🎲 Fair Random Draw")
            self.btn_settle.config(text="✅ Settle All Bets")
            self.btn_reset_draw.config(text="Reset Draw")
        else:
            self.header_title.config(text="★ Lucky48 庄家总控与投注结算平台")
            self.header_date_lbl.config(text="开奖日期:")
            self.notebook.tab(0, text="🎲 开奖生成与控盘")
            self.notebook.tab(1, text="📊 全盘汇总")
            self.notebook.tab(2, text="📥 客户注单管理")
            self.notebook.tab(3, text="✍️ 庄家录单")
            self.notebook.tab(4, text="⚙️ 规则与生肖")
            self.notebook.tab(5, text="📑 报表对账")
            self.btn_gen_optimized.config(text="⚡ 按控盘赔付率生成 7 个号码")
            self.btn_gen_fair.config(text="🎲 完全随机生成")
            self.btn_settle.config(text="✅ 一键全盘开奖结算")
            self.btn_reset_draw.config(text="重置开奖码")

        self.refresh_all_views()

def main():
    root = tk.Tk()
    app = Lucky48HostApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()