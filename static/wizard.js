/**
 * wizard.js — Handles numeric steppers, chip selectors, and slider live-values.
 * Loaded on all wizard steps.
 */

(function () {
    'use strict';

    // ── Numeric Steppers ───────────────────────────────────────────────────
    document.querySelectorAll('.stepper-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const inputId = btn.dataset.target;
            const op = btn.dataset.op;
            const input = document.getElementById(inputId);
            if (!input) return;

            const step = parseFloat(input.step) || 1;
            const min = parseFloat(input.min) ?? -Infinity;
            const max = parseFloat(input.max) ?? Infinity;
            let val = parseFloat(input.value) || 0;

            val = op === 'inc' ? val + step : val - step;
            val = Math.min(max, Math.max(min, parseFloat(val.toFixed(2))));
            input.value = val;

            // Fire change event for any listeners
            input.dispatchEvent(new Event('input', { bubbles: true }));
        });
    });

    // ── Chip / Segmented Controls ──────────────────────────────────────────
    document.querySelectorAll('.chip').forEach(chip => {
        chip.addEventListener('click', () => {
            const target = chip.dataset.target;
            const value = chip.dataset.value;

            // Deactivate siblings
            document.querySelectorAll(`.chip[data-target="${target}"]`).forEach(c => {
                c.classList.remove('chip--active');
                c.setAttribute('aria-pressed', 'false');
            });

            chip.classList.add('chip--active');
            chip.setAttribute('aria-pressed', 'true');

            // Write to hidden input
            const hidden = document.getElementById(target);
            if (hidden) hidden.value = value;
        });

        // Keyboard support
        chip.addEventListener('keydown', e => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                chip.click();
            }
        });
        chip.setAttribute('tabindex', '0');
        chip.setAttribute('role', 'radio');
    });

    // ── Client-side form guard: stepper inputs must be in-range ───────────
    const form = document.querySelector('form[id]');
    if (form) {
        form.addEventListener('submit', e => {
            let ok = true;
            form.querySelectorAll('.stepper-input[required]').forEach(inp => {
                const val = parseFloat(inp.value);
                const min = parseFloat(inp.min);
                const max = parseFloat(inp.max);
                if (isNaN(val) || val < min || val > max) {
                    inp.classList.add('input-error');
                    ok = false;
                } else {
                    inp.classList.remove('input-error');
                }
            });
            if (!ok) {
                e.preventDefault();
            }
        });

        // Clear error state on input
        form.querySelectorAll('.stepper-input').forEach(inp => {
            inp.addEventListener('input', () => inp.classList.remove('input-error'));
        });
    }

})();
