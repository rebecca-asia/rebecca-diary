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
            fetchJSON('data/status.json'),
            fetchJSON('data/nurture.json')
        ]).then(function (results) {
            var status = results[0];
            var nurture = results[1];

            renderStatusBar(status);
            renderNurtureMini(nurture);
        });
    }

    // Initial load + 5 minute interval
    updateRoom();
    setInterval(updateRoom, 5 * 60 * 1000);

    // ═══════════════════════════════════════════════════════════════════
    // Language Toggle (JA / EN)
    // ═══════════════════════════════════════════════════════════════════

    var LANG_KEY = 'rebecca-diary-lang';
    var langToggle = document.getElementById('langToggle');

    function setLang(lang) {
        document.documentElement.setAttribute('data-active-lang', lang);
        if (langToggle) {
            var ja = langToggle.querySelector('.lang-label-ja');
            var en = langToggle.querySelector('.lang-label-en');
            if (ja) ja.classList.toggle('lang-active', lang === 'ja');
            if (en) en.classList.toggle('lang-active', lang === 'en');
        }
        try { localStorage.setItem(LANG_KEY, lang); } catch (e) {}
    }

    // Restore saved preference (default: ja)
    var savedLang = 'ja';
    try { savedLang = localStorage.getItem(LANG_KEY) || 'ja'; } catch (e) {}
    setLang(savedLang);

    if (langToggle) {
        langToggle.addEventListener('click', function () {
            var current = document.documentElement.getAttribute('data-active-lang') || 'ja';
            setLang(current === 'ja' ? 'en' : 'ja');
        });
    }

})();
