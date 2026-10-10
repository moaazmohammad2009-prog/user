"""
Core Engine for 48-Pick-7 Lottery & Bet Settlement System.

Handles zodiac mappings, bet types, configuration management,
bet settlement execution, and risk-controlled draw generation algorithms.
"""

import json
import logging
import os
import random
from typing import Any, Dict, List, Optional, Tuple, Set

# Configure logger for core operations
logger = logging.getLogger("LotteryCore")

TOTAL_NUMBERS: int = 48
DRAW_COUNT: int = 7

DEFAULT_ZODIACS: Dict[int, Dict[str, Any]] = {
    1: {"name_zh": "鼠", "name_en": "Rat", "numbers": [1, 13, 25, 37]},
    2: {"name_zh": "牛", "name_en": "Ox", "numbers": [2, 14, 26, 38]},
    3: {"name_zh": "虎", "name_en": "Tiger", "numbers": [3, 15, 27, 39]},
    4: {"name_zh": "兔", "name_en": "Rabbit", "numbers": [4, 16, 28, 40]},
    5: {"name_zh": "龙", "name_en": "Dragon", "numbers": [5, 17, 29, 41]},
    6: {"name_zh": "蛇", "name_en": "Snake", "numbers": [6, 18, 30, 42]},
    7: {"name_zh": "马", "name_en": "Horse", "numbers": [7, 19, 31, 43]},
    8: {"name_zh": "羊", "name_en": "Goat", "numbers": [8, 20, 32, 44]},
    9: {"name_zh": "猴", "name_en": "Monkey", "numbers": [9, 21, 33, 45]},
    10: {"name_zh": "鸡", "name_en": "Rooster", "numbers": [10, 22, 34, 46]},
    11: {"name_zh": "狗", "name_en": "Dog", "numbers": [11, 23, 35, 47]},
    12: {"name_zh": "猪", "name_en": "Pig", "numbers": [12, 24, 36, 48]},
}

DEFAULT_BET_TYPES: Dict[str, Dict[str, Any]] = {
    "TM": {
        "id": "TM",
        "name_zh": "特码",
        "name_en": "Main Number (TM)",
        "category": "only_mn",
        "pay_ratio": 50.0,
        "input_type": "number",
        "count": 1,
        "desc_zh": "猜第7位特码 (1-48)",
        "desc_en": "Pick the 7th Main Number (1-48)",
        "target_prob": 2.08,
    },
    "TX": {
        "id": "TX",
        "name_zh": "特肖",
        "name_en": "Main Zodiac (TX)",
        "category": "only_mn",
        "pay_ratio": 50.0,
        "input_type": "zodiac",
        "count": 1,
        "desc_zh": "猜特码所属生肖 (Z1-Z12)",
        "desc_en": "Pick Main Number's Zodiac (Z1-Z12)",
        "target_prob": 8.33,
    },
    "TMDS": {
        "id": "TMDS",
        "name_zh": "特码单双",
        "name_en": "Main Odd/Even (TMDS)",
        "category": "only_mn",
        "pay_ratio": 1.0,
        "input_type": "choice",
        "choices": ["单", "双"],
        "count": 1,
        "desc_zh": "特码单双 (单/双)",
        "desc_en": "Main Number Odd or Even",
        "target_prob": 50.0,
    },
    "DX": {
        "id": "DX",
        "name_zh": "特码大小",
        "name_en": "Main High/Low (DX)",
        "category": "only_mn",
        "pay_ratio": 1.0,
        "input_type": "choice",
        "choices": ["大", "小"],
        "count": 1,
        "desc_zh": "特码大小 (大:25-48, 小:1-24)",
        "desc_en": "Main High/Low (High:25-48, Low:1-24)",
        "target_prob": 50.0,
    },
    "PTYX": {
        "id": "PTYX",
        "name_zh": "平特一肖",
        "name_en": "Any 1 Zodiac (PTYX)",
        "category": "all_7",
        "pay_ratio": 1.0,
        "input_type": "zodiac",
        "count": 1,
        "desc_zh": "7个号码中包含该生肖",
        "desc_en": "Pick 1 Zodiac in all 7 numbers",
        "target_prob": 46.0,
    },
    "2LX": {
        "id": "2LX",
        "name_zh": "二连肖",
        "name_en": "2 Zodiacs (2LX)",
        "category": "all_7",
        "pay_ratio": 3.0,
        "input_type": "zodiac",
        "count": 2,
        "desc_zh": "7个号码中包含选中的2个生肖",
        "desc_en": "Pick 2 Zodiacs in all 7 numbers",
        "target_prob": 18.0,
    },
    "3LX": {
        "id": "3LX",
        "name_zh": "三连肖",
        "name_en": "3 Zodiacs (3LX)",
        "category": "all_7",
        "pay_ratio": 10.0,
        "input_type": "zodiac",
        "count": 3,
        "desc_zh": "7个号码中包含选中的3个生肖",
        "desc_en": "Pick 3 Zodiacs in all 7 numbers",
        "target_prob": 6.0,
    },
    "4LX": {
        "id": "4LX",
        "name_zh": "四连肖",
        "name_en": "4 Zodiacs (4LX)",
        "category": "all_7",
        "pay_ratio": 300.0,
        "input_type": "zodiac",
        "count": 4,
        "desc_zh": "7个号码中包含选中的4个生肖",
        "desc_en": "Pick 4 Zodiacs in all 7 numbers",
        "target_prob": 1.5,
    },
    "2Z2": {
        "id": "2Z2",
        "name_zh": "二中二",
        "name_en": "2 of 2 (2Z2)",
        "category": "first_6",
        "pay_ratio": 60.0,
        "input_type": "number",
        "count": 2,
        "desc_zh": "前6个正码中包含选中的2个号码",
        "desc_en": "Pick 2 numbers in first 6 numbers",
        "target_prob": 1.3,
    },
    "3Z3": {
        "id": "3Z3",
        "name_zh": "三中三",
        "name_en": "3 of 3 (3Z3)",
        "category": "first_6",
        "pay_ratio": 600.0,
        "input_type": "number",
        "count": 3,
        "desc_zh": "前6个正码中包含选中的3个号码",
        "desc_en": "Pick 3 numbers in first 6 numbers",
        "target_prob": 0.1,
    },
    "DP": {
        "id": "DP",
        "name_zh": "单平/正码",
        "name_en": "Single Regular (DP)",
        "category": "first_6",
        "pay_ratio": 6.0,
        "input_type": "number",
        "count": 1,
        "desc_zh": "前6个正码中包含选中的1个号码",
        "desc_en": "Pick 1 number in first 6 numbers",
        "target_prob": 12.5,
    },
}


def get_zodiac_for_number(num: int) -> int:
    """Calculates the 1-indexed zodiac ID for a given number."""
    return ((num - 1) % 12) + 1


def _extract_items(val: Any) -> List[Any]:
    """Helper function to normalize variable types into a clean list of values."""
    if isinstance(val, (list, tuple, set)):
        return list(val)
    if isinstance(val, int):
        return [val]
    if isinstance(val, str):
        cleaned = val.replace(";", " ").replace(",", " ")
        tokens = [x.strip() for x in cleaned.split() if x.strip()]
        if tokens and all(t.isdigit() for t in tokens):
            return [int(t) for t in tokens]
        return tokens if len(tokens) > 1 else [val.strip()]
    return [val]


class BetManager:
    """Core domain logic manager handling bets processing, system settings, and draw calculations."""

    def __init__(self, config_path: Optional[str] = None) -> None:
        self.zodiacs: Dict[int, Dict[str, Any]] = dict(DEFAULT_ZODIACS)
        self.bet_types: Dict[str, Dict[str, Any]] = dict(DEFAULT_BET_TYPES)
        self.config_path: Optional[str] = config_path

        if config_path and os.path.exists(config_path):
            self.load_config(config_path)

    def load_config(self, filepath: str) -> None:
        """Loads configuration overrides from JSON."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "zodiacs" in data:
                    self.zodiacs = {int(k): v for k, v in data["zodiacs"].items()}
                if "bet_types" in data:
                    self.bet_types = data["bet_types"]
            logger.info("Configuration successfully loaded from %s", filepath)
        except Exception as err:
            logger.error("Failed to load config file: %s", err)

    def save_config(self, filepath: Optional[str] = None) -> None:
        """Persists internal configurations to disk."""
        target = filepath or self.config_path
        if not target:
            logger.warning("No file path specified for saving configuration.")
            return
        try:
            data = {"zodiacs": self.zodiacs, "bet_types": self.bet_types}
            with open(target, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info("Configuration saved to %s", target)
        except Exception as err:
            logger.error("Error saving config file: %s", err)

    def get_zodiac_name(self, z_id: int, lang: str = "zh") -> str:
        entry = self.zodiacs.get(z_id, {})
        return entry.get(f"name_{lang}", f"Z{z_id}")

    def get_number_zodiac_name(self, num: int, lang: str = "zh") -> str:
        return self.get_zodiac_name(get_zodiac_for_number(num), lang)

    def update_zodiac_name(self, z_id: int, name_zh: str, name_en: str) -> None:
        if z_id in self.zodiacs:
            self.zodiacs[z_id]["name_zh"] = name_zh.strip()
            self.zodiacs[z_id]["name_en"] = name_en.strip()

    def update_bet_type(
        self,
        bet_id: str,
        name_zh: str,
        name_en: str,
        pay_ratio: float,
        target_prob: float = 50.0,
    ) -> None:
        if bet_id in self.bet_types:
            self.bet_types[bet_id].update({
                "name_zh": name_zh,
                "name_en": name_en,
                "pay_ratio": float(pay_ratio),
                "target_prob": float(target_prob),
            })

    def add_custom_bet_type(
        self,
        bet_id: str,
        name_zh: str,
        name_en: str,
        category: str,
        pay_ratio: float,
        input_type: str,
        count: int,
        desc_zh: str = "",
        desc_en: str = "",
    ) -> None:
        self.bet_types[bet_id] = {
            "id": bet_id,
            "name_zh": name_zh,
            "name_en": name_en,
            "category": category,
            "pay_ratio": float(pay_ratio),
            "input_type": input_type,
            "count": int(count),
            "desc_zh": desc_zh,
            "desc_en": desc_en,
            "target_prob": 50.0,
        }

    def remove_bet_type(self, bet_id: str) -> None:
        self.bet_types.pop(bet_id, None)

    def settle_bet(self, bet: Dict[str, Any], draw_numbers: List[int]) -> Dict[str, Any]:
        """Settles a single user bet entry against selected draw numbers."""
        if len(draw_numbers) != DRAW_COUNT:
            raise ValueError(f"Expected {DRAW_COUNT} numbers, received {len(draw_numbers)}")

        first_6: Set[int] = set(draw_numbers[:6])
        mn: int = draw_numbers[6]
        all_7: Set[int] = set(draw_numbers)
        mn_zodiac: int = get_zodiac_for_number(mn)
        all_7_zodiacs: Set[int] = {get_zodiac_for_number(n) for n in draw_numbers}

        bet_type_id = bet.get("bet_type", "")
        bet_def = self.bet_types.get(bet_type_id, {})
        ratio = float(bet.get("pay_ratio", bet_def.get("pay_ratio", 1.0)))
        bet_amount = float(bet.get("bet_amount", 0.0))
        pick = bet.get("selection")

        category = bet_def.get("category", "")
        won = False
        info = ""

        # Processing category rules
        if category == "only_mn":
            items = _extract_items(pick)
            if bet_type_id == "TM":
                target = int(items[0]) if items else 0
                won = (mn == target)
                info = f"Mn={mn}, Pick={target}"
            elif bet_type_id == "TX":
                target_z = int(items[0]) if items else 0
                won = (mn_zodiac == target_z)
                info = f"Mn={mn}(Z{mn_zodiac}), Pick=Z{target_z}"
            elif bet_type_id == "TMDS":
                choice = str(pick).strip()
                is_odd = (mn % 2 == 1)
                won = is_odd if choice in ("单", "Odd", "odd") else not is_odd
                info = f"Mn={mn}"
            elif bet_type_id == "DX":
                choice = str(pick).strip()
                is_high = (mn >= 25)
                won = is_high if choice in ("大", "High", "high") else not is_high
                info = f"Mn={mn}"
            else:
                target = int(items[0]) if items and str(items[0]).isdigit() else -1
                won = (mn == target)

        elif category == "all_7":
            items = _extract_items(pick)
            if bet_type_id == "PTYX":
                target_z = int(items[0]) if items else 0
                won = (target_z in all_7_zodiacs)
                info = f"Pick=Z{target_z}"
            elif bet_type_id in ("2LX", "3LX", "4LX"):
                targets = {int(z) for z in items}
                won = targets.issubset(all_7_zodiacs)
                info = f"Hits={len(targets & all_7_zodiacs)}/{len(targets)}"
            else:
                targets = {int(x) for x in items if str(x).isdigit()}
                won = targets.issubset(
                    all_7_zodiacs if all(x <= 12 for x in targets) else all_7
                )

        elif category == "first_6":
            items = _extract_items(pick)
            if bet_type_id == "DP":
                target = int(items[0]) if items else 0
                won = (target in first_6)
                info = f"Pick={target}"
            elif bet_type_id in ("2Z2", "3Z3"):
                targets = {int(n) for n in items}
                won = targets.issubset(first_6)
                info = f"Hits={len(targets & first_6)}/{len(targets)}"
            else:
                targets = {int(n) for n in items}
                won = targets.issubset(first_6)

        payout = bet_amount * ratio if won else 0.0
        net = payout - bet_amount

        res = dict(bet)
        res.update({
            "settled": True,
            "won": won,
            "status": "WIN" if won else "LOSE",
            "payout": payout,
            "net_profit": net,
            "match_info": info,
        })
        return res

    def settle_all_bets(
        self, bets: List[Dict[str, Any]], draw_numbers: List[int]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Processes and calculates outcomes for all active bets."""
        settled_list = []
        total_bet = 0.0
        total_payout = 0.0
        total_net = 0.0
        win_count = 0
        lose_count = 0

        for b in bets:
            s = self.settle_bet(b, draw_numbers)
            settled_list.append(s)
            amount = float(b.get("bet_amount", 0.0))
            total_bet += amount
            total_payout += s["payout"]
            total_net += s["net_profit"]
            if s["won"]:
                win_count += 1
            else:
                lose_count += 1

        summary = {
            "draw_numbers": draw_numbers,
            "first_6": draw_numbers[:6],
            "main_number": draw_numbers[6],
            "total_bets_count": len(bets),
            "win_count": win_count,
            "lose_count": lose_count,
            "win_percentage": round((win_count / len(bets) * 100.0) if bets else 0.0, 2),
            "total_bet_amount": round(total_bet, 2),
            "total_payout": round(total_payout, 2),
            "player_net_profit": round(total_net, 2),
            "house_net_profit": round(-total_net, 2),
            "payout_percentage": round(
                (total_payout / total_bet * 100.0) if total_bet > 0 else 0.0, 2
            ),
        }
        return settled_list, summary

    def generate_draw_numbers(
        self,
        locked_numbers: Optional[Dict[int, int]] = None,
        target_payout_pct: Optional[float] = None,
        all_bets: Optional[List[Dict[str, Any]]] = None,
        candidate_samples: int = 1500,
    ) -> Tuple[List[int], Optional[Dict[str, Any]]]:
        """Generates random or risk-optimized draw combinations."""
        locked = locked_numbers or {}
        locked_vals = set(locked.values())
        pool = [n for n in range(1, TOTAL_NUMBERS + 1) if n not in locked_vals]

        def _draw() -> List[int]:
            sample = random.sample(pool, DRAW_COUNT - len(locked))
            result = [0] * DRAW_COUNT
            idx = 0
            for i in range(DRAW_COUNT):
                if i in locked:
                    result[i] = locked[i]
                else:
                    result[i] = sample[idx]
                    idx += 1
            return result

        if target_payout_pct is None or not all_bets:
            return _draw(), None

        total_pool = sum(float(b.get("bet_amount", 0.0)) for b in all_bets)
        if total_pool <= 0:
            return _draw(), None

        target_amount = (target_payout_pct / 100.0) * total_pool
        best_candidate: Optional[List[int]] = None
        best_diff = float("inf")
        best_stats: Optional[Dict[str, Any]] = None

        for _ in range(candidate_samples):
            cand = _draw()
            _, stats = self.settle_all_bets(all_bets, cand)
            diff = abs(stats["total_payout"] - target_amount)
            if diff < best_diff:
                best_diff = diff
                best_candidate = cand
                best_stats = stats
                if diff == 0:
                    break

        return (best_candidate if best_candidate is not None else _draw()), best_stats


I18N = {
    "zh": {
        "app_title": "48选7 智能彩票与投注结算系统",
        "tab_self_input": "自投录单 (用户端)",
        "tab_upload_bets": "导入客户注单",
        "tab_combined": "所有注单汇总",
        "tab_generator": "开奖结果生成与控盘",
        "tab_settings": "规则与生肖设置",
        "tab_reports": "报表与导出",
        "client_name": "客户姓名",
        "bet_date": "投注日期",
        "device_id": "设备ID",
        "timestamp": "时间戳",
        "bet_line": "行号",
        "game_type": "玩法类型",
        "selection": "投注内容",
        "bet_unit": "投注金额",
        "possible_payout": "预计最高奖金",
        "actions": "操作",
        "add_bet": "添加投注",
        "remove": "删除",
        "confirm": "确认提交",
        "clear": "清空",
        "export_json": "导出 JSON",
        "export_csv": "导出 CSV",
        "import_file": "导入文件",
        "total_bets": "总注数",
        "total_bet_amount": "投注总额",
        "total_possible_payout": "预计总赔付",
        "win_lose_status": "结算状态",
        "win_amount": "中奖金额",
        "net_profit": "盈亏净额",
        "draw_numbers": "开奖号码 (7码)",
        "main_number": "特码 (第7码)",
        "regular_numbers": "正码 (前6码)",
        "generate_random": "随机生成号码",
        "lock_number": "锁定/自选手选号码",
        "payout_slider": "开奖目标赔付比例控盘 (1-100% 档位)",
        "slider_label": "赔付率控盘档位 (1-100)",
        "run_settlement": "一键开奖结算",
        "house_net_profit": "庄家盈利",
        "player_win_rate": "客户胜率",
        "switch_lang": "Switch to English",
        "win_tag": "中奖",
        "lose_tag": "未中",
        "odd": "单",
        "even": "双",
        "high": "大",
        "low": "小",
        "zodiac": "生肖",
        "number": "号码",
        "handpick_hint": "可手工固定1个或多个号码，其余号码由系统控盘算法生成",
        "payout_ratio": "赔率",
        "target_prob": "预设胜率 %",
        "save_settings": "保存设置",
        "reset_defaults": "恢复默认",
    },
    "en": {
        "app_title": "Lucky48 Lottery & Bet Management System",
        "tab_self_input": "Self Input Bets (User)",
        "tab_upload_bets": "Upload Client Bets",
        "tab_combined": "Combined All Bets",
        "tab_generator": "Draw Generator & Payout Control",
        "tab_settings": "Rules & Zodiac Settings",
        "tab_reports": "Reports & Export",
        "client_name": "Client Name",
        "bet_date": "Bet Date",
        "device_id": "Device ID",
        "timestamp": "Timestamp",
        "bet_line": "Line #",
        "game_type": "Game Type",
        "selection": "Selection",
        "bet_unit": "Bet Unit",
        "possible_payout": "Possible Payout",
        "actions": "Actions",
        "add_bet": "Add Bet",
        "remove": "Remove",
        "confirm": "Confirm & Save",
        "clear": "Clear All",
        "export_json": "Export JSON",
        "export_csv": "Export CSV",
        "import_file": "Import File",
        "total_bets": "Total Bets",
        "total_bet_amount": "Total Bet Amount",
        "total_possible_payout": "Total Possible Payout",
        "win_lose_status": "Status",
        "win_amount": "Win Payout",
        "net_profit": "Net Win/Lose",
        "draw_numbers": "Draw Numbers (7 Balls)",
        "main_number": "Main Number (7th)",
        "regular_numbers": "Regular Numbers (1st-6th)",
        "generate_random": "Generate Random Draw",
        "lock_number": "Lock / Handpick Numbers",
        "payout_slider": "Payout Percentage Control Bar (1-100 Level)",
        "slider_label": "Target Payout Level (1-100%)",
        "run_settlement": "Generate & Settle All",
        "house_net_profit": "House Net Profit",
        "player_win_rate": "Player Win %",
        "switch_lang": "切换为中文",
        "win_tag": "WIN",
        "lose_tag": "LOSE",
        "odd": "Odd",
        "even": "Even",
        "high": "High",
        "low": "Low",
        "zodiac": "Zodiac",
        "number": "Number",
        "handpick_hint": "Handpick/lock 1 or more numbers; generator optimizes remaining numbers",
        "payout_ratio": "Payout Ratio",
        "target_prob": "Preset Win %",
        "save_settings": "Save Settings",
        "reset_defaults": "Reset Defaults",
    },
}