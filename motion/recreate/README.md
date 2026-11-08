# Recreations of reference motion graphics

Goal (Andrew, Nov 8): match the reference animations nearly picture-perfect so we lock the motion-graphic style, then turn the techniques into a skill.

- Each recreation: `motion/recreate/<ref-id>/index.html` exposing `window.render(t)` (pure function of time; no timers, no CSS transitions), plus `notes.md` (measured timings, easing, sizes, colours, blur/shadow values, what's still off).
- Render: `node motion/recreate/shoot.js <html> <framesdir> <dur> <fps> <w> <h>`
- Compare to the reference: `bash motion/recreate/compare.sh /home/user/work/refs/<id>.mp4 <start> <dur> <framesdir> <fps> <outprefix>` → side-by-side (ref | ours | difference) video + SSIM.
- References: `/home/user/work/refs/*.mp4`, breakdowns in `docs/brand-video/library/`.
