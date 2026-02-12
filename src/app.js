// Rebecca's Diary — Interactions
(function () {
    'use strict';

    // ─── Mascot Click: Expression Cycler ────────────────────────────
    var mascot = document.getElementById('mascot');
    var expressions = [
        'assets/rebecca/レベッカ_顔絵ニュートラル.png',
        'assets/rebecca/レベッカ_ウィンク.png',
        'assets/rebecca/レベッカ_微笑.png',
        'assets/rebecca/レベッカ_見下し.png',
        'assets/rebecca/レベッカ_すね顔.png',
        'assets/rebecca/レベッカ_ガッツポーズ.png',
        'assets/rebecca/レベッカ_coffee.png',
        'assets/rebecca/レベッカ_呆れ顔.png',
        'assets/rebecca/レベッカ_コミカル中指.png',
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

})();
