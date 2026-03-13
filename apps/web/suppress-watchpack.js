/**
 * Suppress Watchpack / scandir ENOMEM noise on Docker Desktop for Windows.
 *
 * The 9P filesystem bridge used for bind-mounts intermittently returns
 * ENOMEM from scandir().  When this bubbles up through Watchpack or as
 * an unhandled rejection it can stall the Next.js compilation pipeline.
 *
 * This preload script (loaded via NODE_OPTIONS="--require …"):
 *   1. Filters "Watchpack Error" messages from console.error
 *   2. Catches unhandled ENOMEM rejections to prevent the server from
 *      hanging on failed scandir() calls
 */

'use strict';

// ── 1. Suppress "Watchpack Error" console.error messages ────────────
const _origError = console.error;

console.error = function (...args) {
  for (let i = 0; i < args.length; i++) {
    const a = args[i];
    if (typeof a === 'string' && a.includes('Watchpack Error')) return;
  }
  return _origError.apply(console, args);
};

// ── 2. Catch unhandled ENOMEM rejections so the server doesn't stall ─
process.on('unhandledRejection', (reason) => {
  if (reason && reason.code === 'ENOMEM') {
    // Silently swallow ENOMEM from scandir — cosmetic on Docker Desktop 9P
    return;
  }
});
