// script.js
(() => {
  'use strict';

  const STORAGE_KEYS = {
    DEVICE_ID: 'lucky48_device_id',
    CLIENT_SLIPS: 'lucky48_client_slips',
    DRAW_NUMBERS: 'lucky48_draw_numbers',
    DRAW_TIMESTAMP: 'lucky48_draw_timestamp'
  };

  const DICT = {
    zh: {
      dashboard: "Lucky48 投注面板",
      clientInfo: "📋 客户与日期信息",
      date: "投注日期",
      client: "客户姓名",
      device: "设备编号:",
      selectGame: "选择玩法",
      betUnit: "投注金额",
      maxPayout: "预计最高奖金",
      presetProb: "预设概率",
      addSlip: "➕ 添加注单",
      currentSlips: (n) => `📑 当前注单明细 (${n} 行)`,
      row: "行号",
      game: "玩法",
      selection: "投注内容",
      amount: "金额",
      payout: "预计奖金",
      result: "结果/盈亏",
      clear: "清空注单",
      exportJson: "💾 导出 JSON",
      exportCsv: "📄 导出 CSV",
      importJson: "📁 导入主机结算",
      tSlips: "总注数",
      tBet: "投注总额",
      tMax: "预计最高赔付",
      tActual: "实际中奖 / 盈亏",
      pending: "待开奖",
      win: "中奖",
      lose: "未中",
      pay: "赔率"
    },
    en: {
      dashboard: "Lucky48 Dashboard",
      clientInfo: "📋 Client & Date Info",
      date: "Bet Date",
      client: "Client Name",
      device: "Device ID:",
      selectGame: "Select Game Type",
      betUnit: "Bet Unit",
      maxPayout: "Possible Payout",
      presetProb: "Preset Prob",
      addSlip: "➕ Add to Slip",
      currentSlips: (n) => `📑 Current Slips (${n} Rows)`,
      row: "Row",
      game: "Game",
      selection: "Selection",
      amount: "Amount",
      payout: "Payout",
      result: "Result/P&L",
      clear: "Clear Slips",
      exportJson: "💾 Export JSON",
      exportCsv: "📄 Export CSV",
      importJson: "📁 Import Host Results",
      tSlips: "Total Slips",
      tBet: "Total Bet",
      tMax: "Max Payout",
      tActual: "Actual P&L",
      pending: "Pending",
      win: "WIN",
      lose: "LOSE",
      pay: "Pay"
    }
  };

  const DEFAULT_ZODIACS = {
    1: { zh: "鼠", en: "Rat", numbers: [1, 13, 25, 37] },
    2: { zh: "牛", en: "Ox", numbers: [2, 14, 26, 38] },
    3: { zh: "虎", en: "Tiger", numbers: [3, 15, 27, 39] },
    4: { zh: "兔", en: "Rabbit", numbers: [4, 16, 28, 40] },
    5: { zh: "龙", en: "Dragon", numbers: [5, 17, 29, 41] },
    6: { zh: "蛇", en: "Snake", numbers: [6, 18, 30, 42] },
    7: { zh: "马", en: "Horse", numbers: [7, 19, 31, 43] },
    8: { zh: "羊", en: "Goat", numbers: [8, 20, 32, 44] },
    9: { zh: "猴", en: "Monkey", numbers: [9, 21, 33, 45] },
    10: { zh: "鸡", en: "Rooster", numbers: [10, 22, 34, 46] },
    11: { zh: "狗", en: "Dog", numbers: [11, 23, 35, 47] },
    12: { zh: "猪", en: "Pig", numbers: [12, 24, 36, 48] }
  };

  const getZodiacsConfig = () => {
    try {
      const raw = localStorage.getItem('lucky48_zodiac_config');
      if (raw) {
        const parsed = JSON.parse(raw);
        if (parsed && typeof parsed === 'object') return parsed;
      }
    } catch (e) {}
    return DEFAULT_ZODIACS;
  };

  const GAME_TYPES = Object.freeze([
    { id: "TM", name_zh: "特码", name_en: "Special Number", category: "only_mn", ratio: 50.0, input: "num", count: 1, prob: "2.08%", desc_zh: "猜第7位特码 (1-48)，中奖赔率 1:50", desc_en: "Pick Special Number (1-48), Pay 1:50" },
    { id: "TX", name_zh: "特肖", name_en: "Special Zodiac", category: "only_mn", ratio: 50.0, input: "zodiac_balls", count: 1, prob: "8.33%", desc_zh: "选择特码所属生肖，赔率 1:50", desc_en: "Pick Special Zodiac, Pay 1:50" },
    { id: "TMDS", name_zh: "特码单双", name_en: "Special Odd/Even", category: "only_mn", ratio: 1.0, input: "choice", choices: ["单", "双"], count: 1, prob: "50%", desc_zh: "特码单双 (单/双)，赔率 1:1", desc_en: "Special Number Odd/Even, Pay 1:1" },
    { id: "DX", name_zh: "特码大小", name_en: "Special Big/Small", category: "only_mn", ratio: 1.0, input: "choice", choices: ["大", "小"], count: 1, prob: "50%", desc_zh: "特码大小 (大:25-48, 小:1-24)，赔率 1:1", desc_en: "Special High/Low, Pay 1:1" },
    { id: "PTYX", name_zh: "平特一肖", name_en: "Flat Zodiac", category: "all_7", ratio: 1.0, input: "zodiac_balls", count: 1, prob: "46%", desc_zh: "7个号码中通过选生肖即中奖，赔率 1:1", desc_en: "Flat Zodiac in 7 balls, Pay 1:1" },
    { id: "2LX", name_zh: "二连肖", name_en: "2 Zodiac Combo", category: "all_7", ratio: 3.0, input: "zodiac_balls", count: 2, prob: "18%", desc_zh: "选2个生肖同时出现，赔率 1:3", desc_en: "Pick 2 Zodiacs, Pay 1:3" },
    { id: "3LX", name_zh: "三连肖", name_en: "3 Zodiac Combo", category: "all_7", ratio: 10.0, input: "zodiac_balls", count: 3, prob: "6%", desc_zh: "选3个生肖同时出现，赔率 1:10", desc_en: "Pick 3 Zodiacs, Pay 1:10" },
    { id: "4LX", name_zh: "四连肖", name_en: "4 Zodiac Combo", category: "all_7", ratio: 300.0, input: "zodiac_balls", count: 4, prob: "1.5%", desc_zh: "选4个生肖同时出现，赔率 1:300", desc_en: "Pick 4 Zodiacs, Pay 1:300" },
    { id: "2Z2", name_zh: "二中二", name_en: "2 Numbers Combo", category: "first_6", ratio: 60.0, input: "num", count: 2, prob: "4.2%", desc_zh: "前6个正码中选2个数字，赔率 1:60", desc_en: "Pick 2 Numbers in first 6, Pay 1:60" },
    { id: "3Z3", name_zh: "三中三", name_en: "3 Numbers Combo", category: "first_6", ratio: 600.0, input: "num", count: 3, prob: "0.8%", desc_zh: "前6个正码中选3个数字，赔率 1:600", desc_en: "Pick 3 Numbers in first 6, Pay 1:600" },
    { id: "DP", name_zh: "单平/正码", name_en: "Regular Number", category: "first_6", ratio: 6.0, input: "num", count: 1, prob: "12.5%", desc_zh: "前6个正码中包含该号码，赔率 1:6", desc_en: "Regular Number in first 6, Pay 1:6" }
  ]);

  const AppState = {
    lang: 'zh',
    selectedGameType: GAME_TYPES[0],
    selectedItems: [],
    betsList: [],
    deviceId: ''
  };

  const getZodiacForNum = (n) => ((n - 1) % 12) + 1;
  const isValidDraw = (draw) => Array.isArray(draw)
    && draw.length === 7
    && draw.every(n => Number.isInteger(n) && n >= 1 && n <= 48)
    && new Set(draw).size === 7;

  const saveToLocalStorage = () => {
    try {
      const clientName = document.getElementById('input-client')?.value.trim() || 'Client User';
      let clientSlipsMap = {};
      const rawMap = localStorage.getItem(STORAGE_KEYS.CLIENT_SLIPS);
      if (rawMap) {
        try { clientSlipsMap = JSON.parse(rawMap) || {}; } catch (e) {}
      }

      Object.entries(clientSlipsMap).forEach(([key, slip]) => {
        if (key === AppState.deviceId
          || (slip && String(slip.deviceId || slip.device_id || key) === AppState.deviceId)) {
          delete clientSlipsMap[key];
        }
      });

      if (AppState.betsList.length) {
        clientSlipsMap[AppState.deviceId] = {
          clientName,
          deviceId: AppState.deviceId,
          bets: AppState.betsList
        };
      }

      localStorage.setItem(STORAGE_KEYS.CLIENT_SLIPS, JSON.stringify(clientSlipsMap));
    } catch (e) {}
  };

  const getBetIdentity = bet => {
    if (bet.bet_id) return `id:${bet.bet_id}`;
    return JSON.stringify([
      bet.line ?? bet.line_number ?? '',
      bet.timestamp || bet.created_at || '',
      bet.client || bet.client_name || '',
      bet.bet_type || '',
      bet.selection,
      bet.bet_amount || bet.stake_amount || bet.bet_unit || 0
    ]);
  };

  const readImportFile = file => new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result || ''));
    reader.onerror = () => reject(reader.error || new Error(`Could not read ${file.name}`));
    reader.readAsText(file);
  });

  const importClientHistory = async event => {
    const input = event.target;
    const file = input.files?.[0];
    if (!file) return;

    try {
      const data = JSON.parse(await readImportFile(file));
      let importedBets = [];
      let drawNumbers = data.draw_numbers;
      let drawTimestamp = data.draw_timestamp || data.export_date;

      if (data.client_slips && typeof data.client_slips === 'object') {
        Object.entries(data.client_slips).forEach(([key, slip]) => {
          if (!slip) return;
          let deviceId = slip.deviceId || slip.device_id;
          if (!deviceId && key === AppState.deviceId) deviceId = key;
          if (!deviceId && key.startsWith('[')) {
            try {
              const parsedKey = JSON.parse(key);
              if (Array.isArray(parsedKey)) deviceId = parsedKey[0];
            } catch (error) {}
          }
          if (String(deviceId || '') !== AppState.deviceId) return;
          const bets = Array.isArray(slip) ? slip : slip.bets;
          if (Array.isArray(bets)) importedBets.push(...bets.filter(Boolean));
        });
      } else if (Array.isArray(data.bets)) {
        const deviceId = data.device_info?.device_id || data.device_id;
        if (String(deviceId || '') === AppState.deviceId) importedBets = data.bets.filter(Boolean);
      }

      if (!importedBets.length) {
        throw new Error(AppState.lang === 'zh'
          ? '文件中没有此设备的注单。请在 iPhone 上确认设备编号与投注时相同。'
          : 'No bets for this device were found in the file. Confirm the iPhone device ID matches the one used for betting.');
      }

      const uniqueBets = new Map();
      importedBets.forEach(bet => uniqueBets.set(getBetIdentity(bet), bet));
      AppState.betsList = [...uniqueBets.values()];

      if (Object.prototype.hasOwnProperty.call(data, 'draw_numbers')
        || Object.prototype.hasOwnProperty.call(data, 'draw_timestamp')) {
        if (isValidDraw(drawNumbers) && Number.isFinite(Date.parse(drawTimestamp || ''))) {
          localStorage.setItem(STORAGE_KEYS.DRAW_NUMBERS, JSON.stringify(drawNumbers));
          localStorage.setItem(STORAGE_KEYS.DRAW_TIMESTAMP, drawTimestamp);
        } else {
          localStorage.removeItem(STORAGE_KEYS.DRAW_NUMBERS);
          localStorage.removeItem(STORAGE_KEYS.DRAW_TIMESTAMP);
        }
      }

      saveToLocalStorage();
      CoreUI.renderAll();
      CoreUI.updateSummaryFooter();
      alert(AppState.lang === 'zh'
        ? `同步完成：已恢复 ${AppState.betsList.length} 条注单和开奖结果。`
        : `Sync complete: restored ${AppState.betsList.length} bet(s) and draw results.`);
    } catch (error) {
      alert(`${AppState.lang === 'zh' ? '导入失败' : 'Import failed'}: ${error.message}`);
    } finally {
      input.value = '';
    }
  };

  const downloadFile = async (filename, content, type) => {
    const blob = new Blob([content], { type });
    if (window.showSaveFilePicker) {
      try {
        const extension = filename.split('.').pop();
        const handle = await window.showSaveFilePicker({
          suggestedName: filename,
          types: [{ description: `${extension.toUpperCase()} file`, accept: { [type.split(';')[0]]: [`.${extension}`] } }]
        });
        const writable = await handle.createWritable();
        await writable.write(blob);
        await writable.close();
        return;
      } catch (error) {
        if (error.name === 'AbortError') return;
      }
    }

    if (typeof File !== 'undefined' && navigator.canShare && navigator.share) {
      const file = new File([blob], filename, { type });
      if (navigator.canShare({ files: [file] })) {
        try {
          await navigator.share({ files: [file], title: filename });
          return;
        } catch (error) {
          if (error.name === 'AbortError') return;
        }
      }
    }

    try {
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      setTimeout(() => {
        link.remove();
        URL.revokeObjectURL(url);
      }, 60000);
    } catch (error) {
      alert(AppState.lang === 'zh' ? `导出失败：${error.message}` : `Export failed: ${error.message}`);
    }
  };

  const exportClientJSON = async () => {
    const clientName = document.getElementById('input-client')?.value.trim() || 'Client User';
    const exportTime = new Date();
    const data = {
      app_id: 'lucky48',
      schema_version: '1.0.0',
      slip_id: `SLIP-${exportTime.toISOString().replace(/[-:.TZ]/g, '')}-${AppState.deviceId}`,
      device_info: {
        device_id: AppState.deviceId,
        client_name: clientName
      },
      created_at: exportTime.toISOString(),
      bets: AppState.betsList
    };
    await downloadFile(
      `Lucky48_${AppState.deviceId}_${exportTime.toISOString().split('T')[0]}.json`,
      JSON.stringify(data, null, 2),
      'application/json;charset=utf-8'
    );
  };

  const exportClientCSV = async () => {
    const clientName = document.getElementById('input-client')?.value.trim() || 'Client User';
    const exportTime = new Date();
    const slipId = `SLIP-${exportTime.toISOString().replace(/[-:.TZ]/g, '')}-${AppState.deviceId}`;
    const headers = ['slip_id', 'device_id', 'client_name', 'timestamp', 'line_number', 'bet_type', 'category', 'selection', 'pay_ratio', 'stake_amount', 'potential_payout'];
    const escapeCsv = value => `"${String(value ?? '').replace(/"/g, '""')}"`;
    const rows = AppState.betsList.map((bet, index) => [
      slipId,
      AppState.deviceId,
      clientName,
      bet.timestamp || '',
      bet.line || index + 1,
      bet.bet_type || '',
      bet.category || '',
      Array.isArray(bet.selection) ? bet.selection.join('|') : bet.selection,
      bet.pay_ratio || 0,
      bet.bet_amount || bet.bet_unit || 0,
      bet.possible_payout || (bet.bet_amount || bet.bet_unit || 0) * (bet.pay_ratio || 0)
    ].map(escapeCsv).join(','));

    await downloadFile(
      `Lucky48_${AppState.deviceId}_${exportTime.toISOString().split('T')[0]}.csv`,
      [headers.join(','), ...rows].join('\r\n'),
      'text/csv;charset=utf-8'
    );
  };

  const loadFromLocalStorage = () => {
    try {
      AppState.betsList = [];
      const rawMap = localStorage.getItem(STORAGE_KEYS.CLIENT_SLIPS);
      if (rawMap) {
        try {
          const clientSlipsMap = JSON.parse(rawMap) || {};
          const seenBets = new Set();
          Object.entries(clientSlipsMap).forEach(([key, clientObj]) => {
            if (!clientObj) return;
            const deviceId = clientObj.deviceId || clientObj.device_id || key;
            if (String(deviceId) !== AppState.deviceId) return;
            const bets = Array.isArray(clientObj) ? clientObj : clientObj.bets;
            if (!Array.isArray(bets)) return;
            bets.forEach(bet => {
              if (!bet) return;
              const identity = getBetIdentity(bet);
              if (seenBets.has(identity)) return;
              seenBets.add(identity);
              AppState.betsList.push(bet);
            });
          });
        } catch (e) {}
      }

      const rawDraw = localStorage.getItem(STORAGE_KEYS.DRAW_NUMBERS);
      const drawTimestamp = Date.parse(localStorage.getItem(STORAGE_KEYS.DRAW_TIMESTAMP) || '');
      if (rawDraw) {
        try {
          const draw = JSON.parse(rawDraw);
          if (isValidDraw(draw) && Number.isFinite(drawTimestamp)) {
            const first6 = new Set(draw.slice(0, 6));
            const mn = draw[6];
            const allZodiacs = new Set(draw.map(n => getZodiacForNum(n)));
            const mnZodiac = getZodiacForNum(mn);

            AppState.betsList.forEach(b => {
              if (!b) return;
              const betTimestamp = Date.parse(b.timestamp || '');
              if (!Number.isFinite(betTimestamp) || betTimestamp >= drawTimestamp) {
                b.settled = false;
                b.won = false;
                b.payout = 0;
                b.net_profit = 0;
                return;
              }
              let won = false;
              const cat = b.category || "only_mn";
              const bType = b.bet_type || "TM";
              const sel = b.selection;
              const bAmt = b.bet_amount || 0;
              const bRatio = b.pay_ratio || 50;

              if (cat === "only_mn") {
                if (bType === "TM") won = (mn === parseInt(sel));
                else if (bType === "TX") won = (mnZodiac === parseInt(sel));
                else if (bType === "TMDS") won = (sel === "单") ? (mn % 2 !== 0) : (mn % 2 === 0);
                else if (bType === "DX") won = (sel === "大") ? (mn >= 25) : (mn <= 24);
              } else if (cat === "all_7") {
                if (bType === "PTYX") won = allZodiacs.has(parseInt(sel));
                else if (["2LX", "3LX", "4LX"].includes(bType)) {
                  const arr = Array.isArray(sel) ? sel : [sel];
                  won = arr.every(z => allZodiacs.has(parseInt(z)));
                }
              } else if (cat === "first_6") {
                if (bType === "DP") won = first6.has(parseInt(sel));
                else if (["2Z2", "3Z3"].includes(bType)) {
                  const arr = Array.isArray(sel) ? sel : [sel];
                  won = arr.every(n => first6.has(parseInt(n)));
                }
              }
              b.settled = true;
              b.won = won;
              b.payout = won ? (bAmt * bRatio) : 0;
              b.net_profit = won ? b.payout : -bAmt;
            });
            return;
          }
        } catch (e) {}
      }

      // Bets stay pending until the host publishes a draw.
      AppState.betsList.forEach(b => {
        if (b) {
          b.settled = false;
          b.won = false;
          b.payout = 0;
          b.net_profit = 0;
        }
      });
    } catch (e) {}
  };

  const getLocalized = (key, ...args) => {
    const pack = DICT[AppState.lang] || DICT.zh;
    const val = pack[key];
    return typeof val === 'function' ? val(...args) : (val || key);
  };

  const escapeHtml = (str) => String(str).replace(/[&<>"']/g, (m) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m]));

  const CoreUI = {
    syncLanguageButton() {
      const btn = document.getElementById('btn-lang-toggle');
      if (btn) btn.textContent = AppState.lang === 'zh' ? 'English' : '中文';
    },

    applyTranslations() {
      this.syncLanguageButton();
      const mapping = {
        'txt-app-title': 'dashboard',
        'txt-client-info': 'clientInfo',
        'lbl-date': 'date',
        'lbl-client': 'client',
        'lbl-device': 'device',
        'lbl-game-type': 'selectGame',
        'lbl-bet-unit': 'betUnit',
        'lbl-calc-payout': 'maxPayout',
        'lbl-win-rate': 'presetProb',
        'btn-add-bet': 'addSlip',
        'txt-current-bets': 'currentSlips',
        'th-col-line': 'row',
        'th-col-game': 'game',
        'th-col-selection': 'selection',
        'th-col-amount': 'amount',
        'th-col-payout': 'payout',
        'th-col-result': 'result',
        'btn-clear-bets': 'clear',
        'btn-export-json': 'exportJson',
        'btn-export-csv': 'exportCsv',
        'btn-import-trigger': 'importJson',
        'lbl-bottom-total-count': 'tSlips',
        'lbl-bottom-total-amount': 'tBet',
        'lbl-bottom-total-possible': 'tMax',
        'lbl-bottom-total-result': 'tActual'
      };

      for (const [id, key] of Object.entries(mapping)) {
        const el = document.getElementById(id);
        if (el) {
          if (key === 'currentSlips') {
            el.textContent = getLocalized(key, AppState.betsList.length);
          } else {
            el.textContent = getLocalized(key);
          }
        }
      }
    },

    renderAll() {
      loadFromLocalStorage();
      this.applyTranslations();
      this.renderGamePills();
      this.renderSelectionArea();
      this.renderBetsTable();
      this.updateSummaryFooter();
    },

    renderGamePills() {
      const container = document.getElementById('game-types-container');
      if (!container) return;
      container.innerHTML = '';
      
      GAME_TYPES.forEach(gt => {
        const pill = document.createElement('button');
        pill.className = 'game-type-pill' + (gt.id === AppState.selectedGameType.id ? ' active' : '');
        const name = AppState.lang === 'zh' ? gt.name_zh : gt.name_en;
        pill.textContent = `${name} (1:${gt.ratio})`;
        pill.dataset.gtId = gt.id;
        container.appendChild(pill);
      });

      const ratioEl = document.getElementById('val-ratio-badge');
      if (ratioEl) ratioEl.textContent = `${getLocalized('pay')} 1:${AppState.selectedGameType.ratio}`;
      
      const descEl = document.getElementById('game-desc-box');
      if (descEl) descEl.textContent = AppState.lang === 'zh' ? AppState.selectedGameType.desc_zh : AppState.selectedGameType.desc_en;
      
      const probEl = document.getElementById('val-calc-prob');
      if (probEl) probEl.textContent = AppState.selectedGameType.prob;
    },

    renderSelectionArea() {
      const area = document.getElementById('selection-area');
      if (!area) return;
      area.innerHTML = '';
      const isZh = AppState.lang === 'zh';
      const gt = AppState.selectedGameType;
      const zodiacs = getZodiacsConfig();

      if (gt.input === 'num') {
        const hint = document.createElement('div');
        hint.style.cssText = 'font-size:12px; color:var(--text-muted); margin-bottom:6px;';
        hint.textContent = isZh ? `请选 ${gt.count} 个号码 (1-48): (已选 ${AppState.selectedItems.length}/${gt.count})` : `Pick ${gt.count} number(s) (1-48): (${AppState.selectedItems.length}/${gt.count})`;
        area.appendChild(hint);

        const grid = document.createElement('div');
        grid.className = 'numbers-grid';
        for (let i = 1; i <= 48; i++) {
          const btn = document.createElement('button');
          btn.className = 'ball-btn' + (AppState.selectedItems.includes(i) ? ' selected' : '');
          btn.dataset.num = i;
          const zId = getZodiacForNum(i);
          const zObj = zodiacs[zId];
          btn.innerHTML = `${i}<span class="z-name">${escapeHtml(isZh ? (zObj?.zh || '') : (zObj?.en || ''))}</span>`;
          grid.appendChild(btn);
        }
        area.appendChild(grid);

      } else if (gt.input === 'zodiac_balls') {
        const hint = document.createElement('div');
        hint.style.cssText = 'font-size:13px; font-weight:600; margin-bottom:8px; color:var(--gold); display:flex; justify-content:space-between; align-items:center;';
        
        let selectedNames = AppState.selectedItems.map(z => {
          const zObj = zodiacs[z];
          return isZh ? (zObj?.zh || z) : (zObj?.en || z);
        }).join(', ');
        if (!selectedNames) selectedNames = isZh ? '未选择' : 'None';

        hint.innerHTML = `<span>📋 ${isZh ? '请选择' : 'Select'} ${gt.count} ${isZh ? '个生肖' : 'Zodiac(s)'} (${AppState.selectedItems.length}/${gt.count})</span><span style="color:#60a5fa; font-size:12px;">[${selectedNames}]</span>`;
        area.appendChild(hint);

        const grid = document.createElement('div');
        grid.style.cssText = 'display:grid; grid-template-columns:repeat(4, 1fr); gap:8px;';
        
        for (let z = 1; z <= 12; z++) {
          const btn = document.createElement('button');
          const isSelected = AppState.selectedItems.includes(z);
          btn.className = 'ball-btn' + (isSelected ? ' selected' : '');
          btn.style.cssText = `padding:10px 6px; border-radius:10px; border:1px solid ${isSelected ? 'var(--gold)' : 'var(--border-color)'}; background:${isSelected ? 'rgba(234, 179, 8, 0.2)' : 'var(--bg-card)'}; color:var(--text-main); cursor:pointer; display:flex; flex-direction:column; align-items:center; justify-content:center; transition:all 0.2s;`;
          
          const zObj = zodiacs[z];
          const zName = isZh ? (zObj?.zh || z) : (zObj?.en || z);
          const zNums = zObj?.numbers ? zObj.numbers.join(',') : '';
          btn.innerHTML = `<span style="font-size:15px; font-weight:bold;">${zName}</span><span style="font-size:10px; color:var(--text-muted); margin-top:2px;">[${zNums}]</span>`;
          
          btn.dataset.zodiac = z;
          grid.appendChild(btn);
        }
        area.appendChild(grid);

      } else if (gt.input === 'choice') {
        const hint = document.createElement('div');
        hint.style.cssText = 'font-size:13px; font-weight:600; margin-bottom:8px; color:var(--gold);';
        hint.textContent = isZh ? `📌 请选择结果:` : `📌 Make your choice:`;
        area.appendChild(hint);

        const grid = document.createElement('div');
        grid.style.cssText = 'display:grid; grid-template-columns:repeat(2, 1fr); gap:12px; margin-top:4px;';
        
        gt.choices.forEach(ch => {
          const isSelected = AppState.selectedItems.includes(ch);
          const btn = document.createElement('button');
          btn.className = 'binary-btn';
          btn.style.cssText = `padding:14px; font-size:16px; font-weight:bold; border-radius:10px; border:2px solid ${isSelected ? 'var(--gold)' : 'var(--border-color)'}; background:${isSelected ? 'var(--gold)' : 'var(--bg-card)'}; color:${isSelected ? '#000' : 'var(--text-main)'}; cursor:pointer; box-shadow:0 4px 10px rgba(0,0,0,0.3); transition:all 0.2s; text-align:center;`;
          
          let label = ch;
          if (ch === '单') label = isZh ? '🔴 单 (Odd)' : '🔴 Odd (单)';
          if (ch === '双') label = isZh ? '🔵 双 (Even)' : '🔵 Even (双)';
          if (ch === '大') label = isZh ? '🔥 大 (High)' : '🔥 High (大)';
          if (ch === '小') label = isZh ? '❄ 小 (Low)' : '❄️ Low (小)';
          
          btn.textContent = label;
          btn.dataset.choice = ch;
          grid.appendChild(btn);
        });
        area.appendChild(grid);
      }
      this.calcPayout();
    },

    toggleZodiacSelect(z) {
      const gt = AppState.selectedGameType;
      const idx = AppState.selectedItems.indexOf(z);
      if (idx > -1) {
        AppState.selectedItems.splice(idx, 1);
      } else {
        if (AppState.selectedItems.length >= gt.count) {
          if (gt.count === 1) {
            AppState.selectedItems = [z];
          } else {
            AppState.selectedItems.shift();
            AppState.selectedItems.push(z);
          }
        } else {
          AppState.selectedItems.push(z);
        }
      }
      this.renderSelectionArea();
    },

    calcPayout() {
      const amt = parseFloat(document.getElementById('input-bet-amount')?.value) || 0;
      const el = document.getElementById('val-calc-payout');
      if (el) el.textContent = (amt * AppState.selectedGameType.ratio).toFixed(2);
    },

    renderBetsTable() {
      loadFromLocalStorage();
      const tbody = document.getElementById('bets-tbody');
      if (!tbody) return;
      tbody.innerHTML = '';
      const isZh = AppState.lang === 'zh';
      const zodiacs = getZodiacsConfig();

      let totalBet = 0, totalPossible = 0;
      AppState.betsList.forEach((b, idx) => {
        totalBet += b.bet_amount;
        totalPossible += b.possible_payout;

        const tr = document.createElement('tr');
        let selDisp = '';
        if (b.bet_type === 'TX' || b.bet_type === 'PTYX') {
          const zObj = zodiacs[b.selection];
          const zName = isZh ? (zObj?.zh || b.selection) : (zObj?.en || b.selection);
          selDisp = `<span style="font-weight:700; color:var(--gold);">${zName}</span>`;
        } else if (b.bet_type.includes('LX') || Array.isArray(b.selection)) {
          const items = Array.isArray(b.selection) ? b.selection : [b.selection];
          selDisp = items.map(z => {
            const zObj = zodiacs[z];
            return `<span style="font-weight:700; color:var(--gold);">${zObj ? (isZh ? zObj.zh : zObj.en) : z}</span>`;
          }).join(', ');
        } else if (typeof b.selection === 'number') {
          const zId = getZodiacForNum(b.selection);
          const zObj = zodiacs[zId];
          selDisp = `<span style="font-weight:700; color:#ef4444;">${b.selection}</span> (${escapeHtml(isZh ? (zObj?.zh || '') : (zObj?.en || ''))})`;
        } else if (Array.isArray(b.selection)) {
          selDisp = b.selection.map(z => {
            const zObj = zodiacs[z];
            return zObj ? (isZh ? zObj.zh : zObj.en) : z;
          }).join(', ');
        } else {
          selDisp = `<strong style="color:var(--gold); font-size:14px;">${escapeHtml(String(b.selection))}</strong>`;
        }

        let stHtml = `<span style="color:var(--text-muted);">${getLocalized('pending')}</span>`;
        if (b.settled) {
          stHtml = b.won
            ? `<span style="color:var(--color-status-win); font-weight:700;">+¥${(b.payout || 0).toFixed(2)} (${isZh ? '中奖' : 'WIN'})</span>`
            : `<span style="color:var(--color-status-lose);">${getLocalized('lose')}</span>`;
        }

        tr.innerHTML = `
          <td><span class="line-badge">${b.line}</span></td>
          <td><strong>${escapeHtml(b.bet_type)}</strong></td>
          <td>${selDisp}</td>
          <td>¥${b.bet_amount.toFixed(2)}</td>
          <td style="color:#60a5fa;">¥${b.possible_payout.toFixed(2)}</td>
          <td>${stHtml}</td>
          <td><button class="btn-del" data-del="${idx}">✕</button></td>
        `;
        tbody.appendChild(tr);
      });

      const titleEl = document.getElementById('txt-current-bets');
      if (titleEl) titleEl.textContent = getLocalized('currentSlips', AppState.betsList.length);

      if (document.getElementById('bottom-total-count')) document.getElementById('bottom-total-count').textContent = AppState.betsList.length;
      if (document.getElementById('bottom-total-amount')) document.getElementById('bottom-total-amount').textContent = `¥${totalBet.toFixed(2)}`;
      if (document.getElementById('bottom-total-possible')) document.getElementById('bottom-total-possible').textContent = `¥${totalPossible.toFixed(2)}`;
    },

    updateSummaryFooter() {
      let totalActualPL = 0;
      let settledCount = 0;
      AppState.betsList.forEach(b => {
        if (b && b.settled) {
          totalActualPL += b.net_profit;
          settledCount++;
        }
      });

      const resultEl = document.getElementById('bottom-total-result');
      if (resultEl) {
        resultEl.textContent = settledCount
          ? (totalActualPL >= 0 ? '+' : '') + `¥${totalActualPL.toFixed(2)}`
          : '--';
        resultEl.className = `summary-val ${settledCount ? (totalActualPL >= 0 ? 'win' : 'lose') : ''}`;
      }
    }
  };

  const Bindings = {
    init() {
      const btnLang = document.getElementById('btn-lang-toggle');
      if (btnLang) {
        btnLang.onclick = () => {
          AppState.lang = AppState.lang === 'zh' ? 'en' : 'zh';
          CoreUI.renderAll();
          saveToLocalStorage();
        };
      }

      const exportJsonBtn = document.getElementById('btn-export-json');
      if (exportJsonBtn) exportJsonBtn.onclick = exportClientJSON;

      const exportCsvBtn = document.getElementById('btn-export-csv');
      if (exportCsvBtn) exportCsvBtn.onclick = exportClientCSV;

      const importTrigger = document.getElementById('btn-import-trigger');
      const importInput = document.getElementById('file-importer');
      if (importTrigger && importInput) {
        importTrigger.onclick = () => importInput.click();
        importInput.onchange = importClientHistory;
      }

      const gtContainer = document.getElementById('game-types-container');
      if (gtContainer) {
        gtContainer.onclick = (e) => {
          const pill = e.target.closest('.game-type-pill');
          if (!pill) return;
          const gt = GAME_TYPES.find(g => g.id === pill.dataset.gtId);
          if (gt) {
            AppState.selectedGameType = gt;
            AppState.selectedItems = [];
            CoreUI.renderGamePills();
            CoreUI.renderSelectionArea();
          }
        };
      }

      const amtInput = document.getElementById('input-bet-amount');
      if (amtInput) {
        amtInput.oninput = () => CoreUI.calcPayout();
      }

      const clientInput = document.getElementById('input-client');
      if (clientInput) {
        clientInput.oninput = () => saveToLocalStorage();
      }

      document.addEventListener('click', (e) => {
        const btn = e.target.closest('button');
        if (!btn) return;
        
        const valText = btn.textContent.trim();
        if (/^\d+$/.test(valText)) {
          const val = parseInt(valText, 10);
          if ([10, 20, 50, 100, 200, 500, 1000, 2000, 5000].includes(val)) {
            const input = document.getElementById('input-bet-amount');
            if (input) {
              input.value = val;
              CoreUI.calcPayout();
            }
          }
        }
      });

      const selArea = document.getElementById('selection-area');
      if (selArea) {
        selArea.onclick = (e) => {
          const ball = e.target.closest('.ball-btn');
          const zodiacBtn = e.target.closest('button[data-zodiac]');
          const bin = e.target.closest('button[data-choice]');

          if (ball && ball.dataset.num) {
            const num = parseInt(ball.dataset.num, 10);
            const idx = AppState.selectedItems.indexOf(num);
            if (idx > -1) {
              AppState.selectedItems.splice(idx, 1);
            } else {
              if (AppState.selectedItems.length >= AppState.selectedGameType.count) {
                if (AppState.selectedGameType.count === 1) {
                  AppState.selectedItems = [num];
                } else {
                  AppState.selectedItems.shift();
                  AppState.selectedItems.push(num);
                }
              } else {
                AppState.selectedItems.push(num);
              }
            }
            CoreUI.renderSelectionArea();
          } else if (zodiacBtn) {
            const z = parseInt(zodiacBtn.dataset.zodiac, 10);
            CoreUI.toggleZodiacSelect(z);
          } else if (bin) {
            AppState.selectedItems = [bin.dataset.choice];
            CoreUI.renderSelectionArea();
          }
        };
      }

      const addBtn = document.getElementById('btn-add-bet');
      if (addBtn) {
        addBtn.onclick = () => {
          const gt = AppState.selectedGameType;
          let rawSelections = [...AppState.selectedItems];
          
          if (rawSelections.length < gt.count) {
            alert(AppState.lang === 'zh' ? `请选满 ${gt.count} 项` : `Please select ${gt.count} item(s)`);
            return;
          }
          const amt = parseFloat(document.getElementById('input-bet-amount')?.value);
          if (!amt || amt <= 0) {
            alert(AppState.lang === 'zh' ? '请输入有效金额' : 'Enter valid amount');
            return;
          }

          const clientName = document.getElementById('input-client')?.value.trim() || 'Self';
          const dateVal = document.getElementById('input-date')?.value || '';

          const isComboGame = gt.id.includes('LX') || gt.id.includes('Z') || gt.count > 1;

          if (isComboGame) {
            const bet = {
              line: AppState.betsList.length + 1,
              client: clientName,
              client_name: clientName,
              date: dateVal,
              device_id: AppState.deviceId,
              timestamp: new Date().toISOString(),
              bet_type: gt.id,
              category: gt.category,
              pay_ratio: gt.ratio,
              selection: [...rawSelections],
              bet_amount: amt,
              possible_payout: amt * gt.ratio,
              settled: false,
              won: false,
              payout: 0,
              net_profit: 0
            };
            AppState.betsList.push(bet);
          } else {
            rawSelections.forEach(item => {
              const bet = {
                line: AppState.betsList.length + 1,
                client: clientName,
                client_name: clientName,
                date: dateVal,
                device_id: AppState.deviceId,
                timestamp: new Date().toISOString(),
                bet_type: gt.id,
                category: gt.category,
                pay_ratio: gt.ratio,
                selection: item,
                bet_amount: amt,
                possible_payout: amt * gt.ratio,
                settled: false,
                won: false,
                payout: 0,
                net_profit: 0
              };
              AppState.betsList.push(bet);
            });
          }

          AppState.selectedItems = [];
          saveToLocalStorage();
          CoreUI.renderSelectionArea();
          CoreUI.renderBetsTable();
          CoreUI.updateSummaryFooter();
        };
      }

      const tbody = document.getElementById('bets-tbody');
      if (tbody) {
        tbody.onclick = (e) => {
          const delBtn = e.target.closest('.btn-del');
          if (!delBtn) return;
          const idx = parseInt(delBtn.dataset.del, 10);
          AppState.betsList.replace ? null : AppState.betsList.splice(idx, 1);
          AppState.betsList.splice(idx, 1);
          AppState.betsList.forEach((b, i) => b.line = i + 1);
          saveToLocalStorage();
          CoreUI.renderBetsTable();
          CoreUI.updateSummaryFooter();
        };
      }

      const btnClear = document.getElementById('btn-clear-bets');
      if (btnClear) {
        btnClear.onclick = () => {
          if (confirm(AppState.lang === 'zh' ? '确定清空所有注单吗？' : 'Clear all bets?')) {
            AppState.betsList = [];
            saveToLocalStorage();
            CoreUI.renderBetsTable();
            CoreUI.updateSummaryFooter();
          }
        };
      }

      window.addEventListener('storage', () => {
        CoreUI.renderAll();
      });
    }
  };

  window.addEventListener('DOMContentLoaded', () => {
    let devId = localStorage.getItem(STORAGE_KEYS.DEVICE_ID);
    if (!devId) {
      devId = `DEV-${Math.random().toString(36).substr(2,4).toUpperCase()}-${Math.random().toString(36).substr(2,4).toUpperCase()}`;
      localStorage.setItem(STORAGE_KEYS.DEVICE_ID, devId);
    }
    AppState.deviceId = devId;
    ['device-badge', 'val-device-id'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.textContent = devId;
    });

    const dateInput = document.getElementById('input-date');
    if (dateInput && !dateInput.value) {
      dateInput.value = new Date().toISOString().split('T')[0];
    }

    CoreUI.renderAll();
    Bindings.init();
  });
})();