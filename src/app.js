// Rebecca's Diary — Interactions
(function () {
    'use strict';

    // ─── Mascot Click: Expression Cycler ────────────────────────────
    var mascot = document.getElementById('mascot');
    var expressions = [
        'assets/rebecca/anime icon.jpeg',
        'assets/rebecca/transparent/レベッカ_ウィンク.png',
        'assets/rebecca/transparent/レベッカ_微笑.png',
        'assets/rebecca/transparent/レベッカ_見下し.png',
        'assets/rebecca/transparent/レベッカ_すね顔.png',
        'assets/rebecca/transparent/レベッカ_ガッツポーズ.png',
        'assets/rebecca/transparent/レベッカ_coffee.png',
        'assets/rebecca/transparent/レベッカ_呆れ顔.png',
        'assets/rebecca/transparent/レベッカ_コミカル中指.png',
    ];
    var clickCount = 0;

    // Preload images
    expressions.forEach(function (src) {
        var img = new Image();
        img.src = src;
    });

    if (mascot) {
        mascot.addEventListener('click', function () {
            clickCount++;
            var idx = clickCount % expressions.length;
            mascot.src = expressions[idx];
            mascot.classList.remove('mascot-bounce');
            // Force reflow to restart animation
            void mascot.offsetWidth;
            mascot.classList.add('mascot-bounce');
        });
    }

    // ─── Late Night Greeting (02:00–05:00) ──────────────────────────
    var hour = new Date().getHours();
    if (hour >= 2 && hour < 5) {
        var toast = document.getElementById('lateNightToast');
        if (toast) {
            setTimeout(function () {
                toast.hidden = false;
            }, 2000);
            var closeBtn = toast.querySelector('.toast-close');
            if (closeBtn) {
                closeBtn.addEventListener('click', function () {
                    toast.hidden = true;
                });
            }
        }
    }

    // ─── Smooth scroll on entry navigation ──────────────────────────
    window.addEventListener('hashchange', function () {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // ═══════════════════════════════════════════════════════════════════
    // Phase 1: Room Status + Health Dashboard
    // ═══════════════════════════════════════════════════════════════════

    var isFirstLoad = true;

    // ─── Data Fetch (WP-6.1) ──────────────────────────────────────────

    function fetchJSON(url) {
        return fetch(url + '?t=' + Date.now())
            .then(function (res) {
                if (!res.ok) return null;
                return res.json();
            })
            .catch(function (e) {
                console.error('Fetch failed:', url, e);
                return null;
            });
    }

    // ─── Relative Time (WP-6.2a) ──────────────────────────────────────

    function relativeTime(isoString) {
        if (!isoString) return '';
        var then = new Date(isoString);
        var now = new Date();
        var diffMs = now - then;
        if (diffMs < 0) return '';
        var diffMin = Math.floor(diffMs / 60000);
        if (diffMin < 1) return 'たった今';
        if (diffMin < 60) return diffMin + '分前';
        var diffH = Math.floor(diffMin / 60);
        if (diffH < 24) return diffH + '時間前';
        var diffD = Math.floor(diffH / 24);
        return diffD + '日前';
    }

    function formatTime(isoString) {
        if (!isoString) return '';
        var d = new Date(isoString);
        var hh = String(d.getHours()).padStart(2, '0');
        var mm = String(d.getMinutes()).padStart(2, '0');
        return hh + ':' + mm;
    }

    // ─── SVG Icon Helper ────────────────────────────────────────────────

    function svgIcon(name, size) {
        var s = size || 16;
        return '<svg class="icon" width="' + s + '" height="' + s + '"><use href="assets/icons.svg#icon-' + name + '"/></svg>';
    }

    // Map status names to icon IDs
    var statusIconMap = {
        'online': 'status-online',
        'away': 'clock',
        'sleeping': 'status-offline',
        'offline': 'status-offline',
        'loading': 'sync'
    };

    // ─── Status Bar Rendering (WP-6.2, WP-6.5) ───────────────────────

    function renderStatusBar(data) {
        var iconEl = document.getElementById('statusEmoji');
        var label = document.getElementById('statusLabel');
        var time = document.getElementById('statusTime');
        var context = document.getElementById('statusContext');
        var bar = document.querySelector('.room-status');

        if (!data) {
            if (bar) bar.setAttribute('data-status', 'loading');
            if (iconEl) iconEl.innerHTML = svgIcon('sync');
            if (label) label.textContent = 'データ取得中...';
            if (time) time.textContent = '';
            if (context) context.textContent = '';
            return;
        }

        var freshness = data.staleness || 'stale';
        if (freshness === 'dead') {
            if (bar) bar.setAttribute('data-status', 'offline');
            if (iconEl) iconEl.innerHTML = svgIcon('status-offline');
            if (label) label.textContent = 'しばらく応答がないみたい...';
            if (time) time.textContent = relativeTime(data.timestamp);
            if (time) time.title = formatTime(data.timestamp);
            if (context) context.textContent = '';
            return;
        }

        if (freshness === 'stale') {
            if (bar) bar.setAttribute('data-status', data.status || 'offline');
            if (iconEl) iconEl.innerHTML = svgIcon('sync');
            if (label) label.textContent = '接続確認中...';
            if (time) {
                time.textContent = relativeTime(data.timestamp);
                time.title = formatTime(data.timestamp);
            }
            if (context) context.textContent = '';
            return;
        }

        var statusName = data.status || 'offline';
        if (bar) bar.setAttribute('data-status', statusName);
        if (iconEl) iconEl.innerHTML = svgIcon(statusIconMap[statusName] || 'status-offline');
        if (label) label.textContent = data.label || 'いない......';

        if (time) {
            time.textContent = relativeTime(data.last_activity);
            time.title = formatTime(data.last_activity);
        }

        if (context && data.time_context && data.time_context.message) {
            context.textContent = '「' + data.time_context.message + '」';
        } else if (context) {
            context.textContent = '';
        }
    }

    // ─── Health Dashboard Rendering (WP-6.3, WP-6.3a) ────────────────

    function renderHealthDashboard(data) {
        var dashboard = document.getElementById('healthDashboard');
        if (!dashboard) return;

        if (!data) {
            renderMetric('cpu', 0, 'loading', '—', '');
            renderMetric('memory', 0, 'loading', '—', '');
            renderMetric('disk', 0, 'loading', '—', '');
            renderMetric('temperature', 0, 'loading', '—', '');
            renderMetric('uptime', 0, 'loading', '—', '');
            renderOverall(null);
            return;
        }

        var freshness = data.staleness || 'stale';
        var dimmed = freshness === 'stale' || freshness === 'dead';

        // Temperature: hide row if null
        var tempRow = document.getElementById('tempRow');
        if (tempRow) {
            tempRow.style.display = data.temperature ? '' : 'none';
        }

        // CPU
        if (data.cpu) {
            renderMetric('cpu', data.cpu.usage_percent,
                data.cpu.state, data.cpu.label,
                data.cpu.usage_percent.toFixed(1) + '%');
        }

        // Memory
        if (data.memory) {
            renderMetric('memory', data.memory.usage_percent,
                data.memory.state, data.memory.label,
                data.memory.used_gb.toFixed(1) + ' / ' + data.memory.total_gb.toFixed(1) + ' GB');
        }

        // Disk
        if (data.disk) {
            renderMetric('disk', data.disk.usage_percent,
                data.disk.state, data.disk.label,
                data.disk.used_gb + ' / ' + data.disk.total_gb + ' GB');
        }

        // Temperature
        if (data.temperature) {
            renderMetric('temperature', Math.min(data.temperature.celsius, 100),
                data.temperature.state, data.temperature.label,
                data.temperature.celsius.toFixed(1) + '°C');
        }

        // Uptime — map to bar percentage (7 days = 100%)
        if (data.uptime) {
            var uptimePct = Math.min((data.uptime.seconds / (7 * 86400)) * 100, 100);
            renderMetric('uptime', uptimePct,
                data.uptime.state, data.uptime.label,
                data.uptime.display);
        }

        // Overall
        renderOverall(data.overall);

        // Staleness indicator
        if (dimmed) {
            dashboard.style.opacity = '0.5';
        } else {
            dashboard.style.opacity = '';
        }

        isFirstLoad = false;
    }

    function renderMetric(name, percent, state, label, detail) {
        var fill = document.getElementById(name === 'temperature' ? 'tempFill' :
            name === 'memory' ? 'memFill' :
            name + 'Fill');
        var labelEl = document.getElementById(name === 'temperature' ? 'tempLabel' :
            name === 'memory' ? 'memLabel' :
            name + 'Label');
        var detailEl = document.getElementById(name === 'temperature' ? 'tempDetail' :
            name === 'memory' ? 'memDetail' :
            name + 'Detail');
        var row = fill ? fill.closest('.health-metric') : null;

        if (row) row.setAttribute('data-state', state || 'loading');

        if (fill) {
            if (isFirstLoad) {
                // Staggered animation on first load
                var metrics = ['cpu', 'memory', 'disk', 'temperature', 'uptime'];
                var idx = metrics.indexOf(name);
                var delay = idx * 80;
                fill.style.transition = 'none';
                fill.style.width = '0%';
                setTimeout(function () {
                    fill.style.transition = 'width 0.8s ease-out, background-color 0.5s ease';
                    fill.style.width = Math.min(percent, 100) + '%';
                }, 50 + delay);
            } else {
                fill.style.width = Math.min(percent, 100) + '%';
            }
        }

        if (labelEl) labelEl.textContent = label || '—';
        if (detailEl) detailEl.textContent = detail || '';
    }

    // Map overall health state to icon + color class
    var overallIconMap = {
        'excellent': 'status-online',
        'good': 'status-online',
        'normal': 'rebecca',
        'poor': 'alert',
        'bad': 'alert',
        'critical': 'alert'
    };

    function renderOverall(overall) {
        var iconEl = document.getElementById('overallEmoji');
        var label = document.getElementById('overallLabel');
        var message = document.getElementById('healthMessage');
        var container = document.getElementById('healthOverall');

        if (!overall) {
            if (container) container.setAttribute('data-state', 'loading');
            if (iconEl) iconEl.innerHTML = svgIcon('rebecca', 22);
            if (label) label.textContent = '';
            if (message) message.textContent = '';
            return;
        }

        var state = overall.state || 'loading';
        if (container) container.setAttribute('data-state', state);
        if (iconEl) iconEl.innerHTML = svgIcon(overallIconMap[state] || 'rebecca', 22);
        if (label) label.textContent = overall.label || '';
        if (message) message.textContent = overall.message ? '「' + overall.message + '」' : '';
    }

    // ─── Alert Rendering (WP-6.4) ─────────────────────────────────────

    function renderAlert(health) {
        var alert = document.getElementById('roomAlert');
        var msg = document.getElementById('alertMessage');
        if (!alert) return;

        if (!health || !health.alert_level || health.alert_level === 0) {
            alert.hidden = true;
            alert.setAttribute('data-level', '0');
            return;
        }

        var level = health.alert_level;
        var text = health.alert_message || '';

        alert.hidden = false;
        alert.setAttribute('data-level', String(level));
        if (msg) msg.textContent = text ? '「' + text + '」' : '';
    }

    // ─── Mini Nurture Widget (WP-7.1) ────────────────────────────────

    function renderNurtureMini(data) {
        if (!data) return;

        var lvEl = document.getElementById('nmLv');
        var moodEl = document.getElementById('nmMood');
        var expEl = document.getElementById('nmExp');
        var dayEl = document.getElementById('nmDay');

        if (lvEl) lvEl.textContent = 'Lv.' + (data.level || '?');
        if (moodEl && data.mood) {
            moodEl.textContent = '「' + (data.mood.message || '—') + '」';
        }
        if (expEl && data.exp) {
            expEl.textContent = 'EXP ' + (data.exp.current || 0) + '/' + (data.exp.next_level || '?');
        }
        if (dayEl) dayEl.textContent = 'Day ' + (data.day || '?');
    }

    // ─── Update Room (WP-6.6) ─────────────────────────────────────────

    function updateRoom() {
        Promise.all([
            fetchJSON('data/health.json'),
            fetchJSON('data/status.json'),
            fetchJSON('data/nurture.json')
        ]).then(function (results) {
            var health = results[0];
            var status = results[1];
            var nurture = results[2];

            renderStatusBar(status);
            renderHealthDashboard(health);
            renderAlert(health);
            renderNurtureMini(nurture);
        });
    }

    // Initial load + 5 minute interval
    updateRoom();
    setInterval(updateRoom, 5 * 60 * 1000);

})();
