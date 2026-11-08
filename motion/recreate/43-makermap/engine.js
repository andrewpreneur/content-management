// MakerMap "one morphing shape" recreation engine (ref 43-makermap-shapes, 1440x1440).
// Pure function of absolute reference time T (seconds). No timers, no CSS transitions.
// Each segment page calls MM.render(T) with T = segmentStart + t.
(function () {
  const $ = (id) => document.getElementById(id);
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const lerp = (a, b, p) => a + (b - a) * p;
  const mix3 = (c1, c2, p) => c1.map((v, i) => Math.round(lerp(v, c2[i], p)));
  const rgb = (c, a) => (a === undefined ? `rgb(${c[0]},${c[1]},${c[2]})` : `rgba(${c[0]},${c[1]},${c[2]},${a})`);

  // ---- easing toolbox -------------------------------------------------------
  // Damped spring step response (mass 1, natural freq w rad/s, damping ratio z). 0 -> 1, may overshoot.
  function S(tau, w, z) {
    if (tau <= 0) return 0;
    if (z >= 1) return 1 - Math.exp(-w * tau) * (1 + w * tau);
    const wd = w * Math.sqrt(1 - z * z);
    return 1 - Math.exp(-z * w * tau) * (Math.cos(wd * tau) + (z * w / wd) * Math.sin(wd * tau));
  }
  // power ease-out over a window
  const easeOut = (T, t0, d, pw = 2.5) => 1 - Math.pow(1 - clamp((T - t0) / d), pw);
  const easeInOut = (T, t0, d) => { const x = clamp((T - t0) / d); return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
  // cubic-bezier(x1,y1,x2,y2) evaluator
  function bez(x1, y1, x2, y2) {
    return (x) => {
      if (x <= 0) return 0; if (x >= 1) return 1;
      let t = x;
      for (let i = 0; i < 8; i++) {
        const cx = 3 * x1 * t * (1 - t) ** 2 + 3 * x2 * t * t * (1 - t) + t ** 3 - x;
        const dx = 3 * x1 * (1 - t) ** 2 + 6 * (x2 - x1) * t * (1 - t) + 3 * (1 - x2) * t * t;
        if (Math.abs(dx) < 1e-6) break; t -= cx / dx; t = clamp(t);
      }
      return 3 * y1 * t * (1 - t) ** 2 + 3 * y2 * t * t * (1 - t) + t ** 3;
    };
  }
  const standard = bez(0.4, 0, 0.2, 1);
  // a "blur-dissolve" visibility: in over [a,b], out over [c,d]
  function vis(T, a, b, c = Infinity, d = Infinity) {
    const i = clamp((T - a) / (b - a)), o = 1 - clamp((T - c) / (d - c));
    return Math.min(i, o);
  }
  function fade(el, p, blurMax = 10, extra = '') {
    if (!el) return;
    el.style.opacity = p.toFixed(3);
    el.style.filter = p >= 0.999 ? 'none' : `blur(${((1 - p) * blurMax).toFixed(2)}px)`;
    el.style.visibility = p <= 0.001 ? 'hidden' : 'visible';
    if (extra) el.style.transform = extra;
  }
  // time-aware monotone cubic (Fritsch-Carlson) through [T,x,y] keys: smooth, no overshoot
  function mono(ts, ys, T) {
    const n = ts.length;
    if (T <= ts[0]) return ys[0]; if (T >= ts[n - 1]) return ys[n - 1];
    let i = 0; while (ts[i + 1] < T) i++;
    const d = [], m = [];
    for (let k = 0; k < n - 1; k++) d.push((ys[k + 1] - ys[k]) / (ts[k + 1] - ts[k]));
    for (let k = 0; k < n; k++) {
      if (k === 0) m.push(d[0]); else if (k === n - 1) m.push(d[n - 2]);
      else m.push(d[k - 1] * d[k] <= 0 ? 0 : (d[k - 1] + d[k]) / 2);
    }
    for (let k = 0; k < n - 1; k++) {
      if (d[k] === 0) { m[k] = 0; m[k + 1] = 0; continue; }
      const a = m[k] / d[k], b = m[k + 1] / d[k], h = a * a + b * b;
      if (h > 9) { const t = 3 / Math.sqrt(h); m[k] = t * a * d[k]; m[k + 1] = t * b * d[k]; }
    }
    const h = ts[i + 1] - ts[i], u = (T - ts[i]) / h;
    const h00 = 2 * u ** 3 - 3 * u * u + 1, h10 = u ** 3 - 2 * u * u + u, h01 = -2 * u ** 3 + 3 * u * u, h11 = u ** 3 - u * u;
    return h00 * ys[i] + h10 * h * m[i] + h01 * ys[i + 1] + h11 * h * m[i + 1];
  }
  function path(keys, T) {
    const ts = keys.map((k) => k[0]);
    return [mono(ts, keys.map((k) => k[1]), T), mono(ts, keys.map((k) => k[2]), T)];
  }
  const table = (keys, T) => { // piecewise linear
    if (T <= keys[0][0]) return keys[0][1];
    for (let i = 0; i < keys.length - 1; i++) if (T <= keys[i + 1][0]) return lerp(keys[i][1], keys[i + 1][1], (T - keys[i][0]) / (keys[i + 1][0] - keys[i][0]));
    return keys[keys.length - 1][1];
  };

  // ---- palette (pixel-sampled) ---------------------------------------------
  const INK = [22, 21, 26];        // #16151A pill / button
  const INK2 = [20, 21, 26];       // #14151A spinner circle
  const PAPER_IN = [252, 252, 252];// #FCFCFC input
  const PAPER = [253, 253, 253];   // #FDFDFD card
  const ORANGE = [226, 85, 42];    // #E2552A

  // ---- background: warm off-white radial (fit: L = 244 - 12*(r/1000)^1.5, B = L-5) ----
  function bgCSS() {
    const stops = [];
    for (let r = 0; r <= 1100; r += 100) { const L = 244 - 12 * Math.pow(r / 1000, 1.5); stops.push(`rgb(${L.toFixed(1)},${L.toFixed(1)},${(L - 5).toFixed(1)}) ${r}px`); }
    return `radial-gradient(circle at 720px 600px, ${stops.join(',')})`;
  }

  // ---- cursor keyframes: tip position (px), measured per 50 ms ---------------
  const CUR = [
    [0.55, 1300, 1500], [0.75, 1060, 1077], [0.80, 952, 846], [0.85, 943, 818], [0.90, 939, 799], [0.95, 939, 786], [1.00, 938, 776],
    [1.05, 935, 770], [1.10, 930, 765], [1.15, 925, 762], [1.20, 914, 760], [1.25, 898, 759], [1.30, 881, 757], [1.35, 867, 755],
    [1.40, 856, 754], [1.45, 848, 753], [1.50, 843, 752], [1.55, 835, 751], [1.60, 829, 749], [1.65, 829, 750], [1.70, 831, 750],
    [1.85, 831, 751], [1.90, 830, 750], [1.95, 826, 750], [2.00, 822, 749], [2.05, 817, 748], [2.10, 840, 770], [2.15, 885, 790],
    [2.20, 925, 806], [2.25, 958, 822], [2.35, 989, 835], [2.40, 1002, 845], [2.45, 1012, 852], [2.50, 1018, 858], [2.55, 1022, 862],
    [2.60, 1024, 865], [2.65, 1026, 868], [2.75, 1050, 845], [2.85, 1080, 805], [2.95, 1099, 777], [3.00, 1105, 765], [3.05, 1109, 756],
    [3.15, 1113, 744], [3.20, 1114, 741], [3.25, 1114, 738], [3.30, 1114, 736], [3.35, 1111, 735], [3.40, 1109, 734], [3.45, 1106, 732],
    [3.483, 1098, 738], [3.517, 1083, 751], [3.55, 1063, 785], [3.65, 1009, 830], [3.75, 975, 868], [3.85, 955, 888], [3.95, 946, 896],
    [4.20, 945, 899], [4.45, 949, 903], [4.517, 950, 904], [4.55, 962, 914], [4.583, 978, 926], [4.617, 999, 943], [4.683, 1039, 974],
    [4.717, 1059, 990], [4.783, 1140, 1056], [4.817, 1188, 1098], [4.85, 1233, 1140], [4.883, 1274, 1182], [4.917, 1310, 1221],
    [5.0, 1373, 1298], [5.05, 1396, 1332], [5.1, 1412, 1358], [5.15, 1422, 1376], [5.3, 1470, 1440]
  ];
  // click squish of cursor (scale about tip): [start, bottom, end]
  const CLICKS = [[1.52, 1.58, 1.68], [3.02, 3.07, 3.16], [4.24, 4.31, 4.42]];
  function clickScale(T, depth) {
    let s = 1;
    for (const [a, b, c] of CLICKS) {
      if (T > a && T < c) s = T < b ? lerp(1, depth, easeOut(T, a, b - a, 2)) : lerp(depth, 1, easeOut(T, b, c - b, 2));
    }
    return s;
  }

  // typing
  const TYPED = 'verbove';
  const KEYT = [2.0, 2.125, 2.25, 2.375, 2.5, 2.625, 2.75];

  // ---- shape state machine ---------------------------------------------------
  function shapeAt(T) {
    let W = 594, H = 168, R = 84, col = INK, sc = 1, blur = 0, shadowDark = 1, cy = 720;
    // hover grow on logo (0.85 -> 0.97)
    let hover = 1 + 0.024 * easeInOut(T, 0.85, 0.12);
    // logo -> button (spring w=16.4 z=0.59, fitted)
    if (T >= 0.995) {
      const p = S(T - 0.995, 16.36, 0.594);
      W = lerp(594, 748.8, p); H = lerp(168, 161, p);
    }
    // press on button 1.50 -> 1.60 -> release spring
    if (T >= 1.5) {
      const down = lerp(1.024, 0.954, easeOut(T, 1.5, 0.1, 2));
      hover = T < 1.6 ? down : lerp(0.954, 0.998, S(T - 1.6, 22, 0.85));
    }
    sc = hover;
    // button -> input: spring (w=16.7, z=0.63) towards a target that itself relaxes
    // (target = 924 + 186*exp(-t/0.161)) -> fast 38% overshoot then slow settle (fit rms 2px)
    if (T >= 1.878) {
      const tau = T - 1.878;
      const tgW = 926 + 186 * Math.exp(-tau / 0.161);
      W = lerp(748.8, tgW, S(tau, 16.67, 0.625));
      H = lerp(161, 134.5, S(tau, 16, 0.9));
      sc = lerp(sc, 1, clamp((T - 1.85) / 0.2));
      const pc = S(T - 1.875, 22.4, 1);            // colour: critically damped, w=22.4
      col = mix3(INK, PAPER_IN, pc); shadowDark = 1 - pc;
      blur = 5 * Math.sin(Math.PI * clamp((T - 1.87) / 0.19));
    }
    R = H / 2;
    // input -> card (fitted: W w=16.45 z=0.96, H w=16.0 z=0.78)
    if (T >= 3.253) {
      const pw = S(T - 3.253, 16.45, 0.964), ph = S(T - 3.253, 16.03, 0.778);
      W = lerp(926.8, 824, pw); H = lerp(134.5, 552, ph);
      R = lerp(67, 46, clamp(ph));
      col = mix3(PAPER_IN, PAPER, clamp(ph)); shadowDark = 0;
      blur = 3 * Math.sin(Math.PI * clamp((T - 3.26) / 0.2));
    }
    // card -> spinner circle (fitted on mid-threshold edges: W w=14.1 z=0.61 from 4.506; H w=15.0 z=0.49 from 4.524)
    if (T >= 4.5) {
      const pw = S(T - 4.506, 14.09, 0.613), ph = S(T - 4.524, 14.96, 0.487);
      W = lerp(824, 314, pw); H = lerp(552, 314, ph);
      const fr = S(T - 4.5, 24, 1);                 // corner radius catches up to a full circle by ~4.75
      R = lerp(46, Math.min(W, H) / 2, fr); R = Math.min(R, Math.min(W, H) / 2);
      const pc = S(T - 4.49, 19.8, 1);              // colour: critically damped, w=19.8
      col = mix3(PAPER, INK2, pc); shadowDark = pc;
      blur = 7 * Math.sin(Math.PI * clamp((T - 4.5) / 0.24));
    }
    // dark circle closes in around the growing orange dot (spring w=16 z=0.7) and the group rises 65px
    if (T >= 5.625) {
      const d = lerp(314, 108, S(T - 5.625, 16, 0.7));
      W = H = d; R = d / 2;
      cy = 720 - 65 * S(T - 5.66, 12, 1);
      blur = 0;
    }
    return { W, H, R, col, sc, blur, shadowDark, cy };
  }

  function shadowCSS(d) {
    // dark elements throw a deeper, longer shadow; light ones a soft 6-10% one.
    const a1 = lerp(0.07, 0.17, d), a2 = lerp(0.05, 0.12, d);
    return `0 ${lerp(26, 34, d).toFixed(1)}px ${lerp(60, 70, d).toFixed(1)}px rgba(30,30,25,${a1.toFixed(3)}), 0 ${lerp(4, 6, d).toFixed(1)}px ${lerp(10, 14, d).toFixed(1)}px rgba(30,30,25,${a2.toFixed(3)})`;
  }

  // ---- render ----------------------------------------------------------------
  let inited = false;
  function init() {
    $('bg').style.background = bgCSS();
    inited = true;
  }

  function render(T) {
    if (!inited) init();
    const st = shapeAt(T);
    const sh = $('shape');
    const L = 720 - st.W / 2, Tp = st.cy - st.H / 2;
    sh.style.left = L + 'px'; sh.style.top = Tp + 'px';
    sh.style.width = st.W + 'px'; sh.style.height = st.H + 'px';
    sh.style.borderRadius = st.R + 'px';
    sh.style.background = rgb(st.col);
    sh.style.transform = `scale(${st.sc.toFixed(4)})`;
    sh.style.filter = st.blur > 0.05 ? `blur(${st.blur.toFixed(2)}px)` : 'none';
    sh.style.boxShadow = shadowCSS(st.shadowDark);
    sh.style.visibility = T < 5.9 ? 'visible' : 'hidden';

    // logo content (centred) — blur-dissolve out 0.90 -> 1.00
    fade($('logo'), vis(T, -1, -0.5, 0.9, 1.0), 12);
    $('logo').style.left = (st.W / 2) + 'px'; $('logo').style.top = (st.H / 2) + 'px';
    // button label — in 1.10 -> 1.20, out 1.84 -> 1.90
    fade($('btnl'), vis(T, 1.1, 1.2, 1.84, 1.9), 12);
    $('btnl').style.left = (st.W / 2) + 'px'; $('btnl').style.top = (st.H / 2) + 'px';

    // input content — anchored to the LEFT edge (slides as the width spring settles)
    const iv = vis(T, 1.95, 2.05, 3.18, 3.25);
    fade($('inl'), iv, 10);
    $('inl').style.left = '0px'; $('inl').style.top = (st.H / 2) + 'px';
    let n = 0; for (const k of KEYT) if (T >= k) n++;
    $('typed').textContent = TYPED.slice(0, Math.max(1, n));
    const blink = T > 2.94 && T < 2.99;
    $('caret').style.opacity = blink ? 0 : 1;
    // enter key — anchored to the RIGHT edge
    fade($('key'), iv, 10);
    $('key').style.left = (st.W - 23 - 88) + 'px'; $('key').style.top = (st.H / 2 - 44) + 'px';
    const kh = easeOut(T, 2.81, 0.22, 2);
    $('key').style.background = rgb(mix3([241, 241, 238], [23, 23, 28], kh));
    $('keyicon').style.stroke = rgb(mix3([165, 165, 165], [255, 255, 255], kh));
    let ks = 1;
    if (T > 3.02) ks = T < 3.1 ? lerp(1, 0.875, easeOut(T, 3.02, 0.08, 2)) : lerp(0.875, 0.96, S(T - 3.1, 20, 0.8));
    $('key').style.transform = `scale(${ks.toFixed(4)})`;

    // card content — anchored top-left, rows stagger in by 50 ms
    // rows stagger in 60-70 ms apart: blur-dissolve 0.12 s + rise 16px (critically damped w=18)
    const rows = [['r0', 3.34], ['r1', 3.40], ['r2', 3.48], ['r3', 3.50]];
    for (const [id, a] of rows) fade($(id), vis(T, a, a + 0.12, 4.44, 4.54), 10, `translateY(${(16 * (1 - S(T - a, 14, 1))).toFixed(2)}px)`);
    let bs = 1; // That's me press
    if (T > 4.24) bs = T < 4.33 ? lerp(1, 0.93, easeOut(T, 4.24, 0.09, 2)) : lerp(0.93, 0.985, S(T - 4.33, 20, 0.8));
    $('tbtn').style.transform = `scale(${bs.toFixed(4)})`;
    $('tbtn').style.background = rgb(mix3([150, 150, 152], INK, S(T - 3.54, 20, 1)));
    // avatar pops in: scale 0.55 -> 1 (spring w=13, z=0.6) from the row start
    $('avatar').style.transform = `scale(${lerp(0.55, 1, S(T - 3.40, 13, 0.6)).toFixed(4)})`;
    $('card').style.left = '0px'; $('card').style.top = '0px';

    // spinner (content scales with the shape) 4.55 -> 5.6
    const k = Math.max(0.3, 1 - 0.2 * Math.exp(-(T - 4.7) / 0.09)); // spinner scale lags the shape
    const sp = $('spin');
    const spinVis = vis(T, 4.61, 4.68, 5.53, 5.6);
    sp.style.opacity = spinVis; sp.style.visibility = spinVis > 0 ? 'visible' : 'hidden';
    sp.style.left = (st.W / 2) + 'px'; sp.style.top = (st.H / 2) + 'px';
    sp.style.transform = `translate(-50%,-50%) scale(${k.toFixed(4)})`;
    const tail = table([[4.5, 60], [4.7, 140], [4.75, 160], [4.8, 180], [4.85, 200], [4.9, 220], [4.95, 240], [5.0, 260], [5.05, 285], [5.1, 305], [5.2, 350]], T);
    const head = table([[4.5, 325], [4.7, 315], [4.75, 310], [4.8, 310], [4.85, 315], [4.9, 320], [4.95, 335], [5.0, 350], [5.05, 375], [5.1, 405], [5.2, 455]], T);
    const r = 75, a0 = tail * Math.PI / 180, a1 = head * Math.PI / 180;
    const large = (head - tail) > 180 ? 1 : 0;
    $('arc').setAttribute('d', `M ${157 + r * Math.cos(a0)} ${157 + r * Math.sin(a0)} A ${r} ${r} 0 ${large} 1 ${157 + r * Math.cos(a1)} ${157 + r * Math.sin(a1)}`);
    $('arc').style.opacity = 1 - clamp((T - 5.08) / 0.12);
    const cp = easeOut(T, 5.09, 0.27, 2.5);
    const ck = $('check'); ck.style.strokeDashoffset = (1 - cp) * 160;
    ck.style.opacity = T < 5.09 ? 0 : 1;
    const cfo = vis(T, -1, 0, 5.52, 5.6);
    ck.style.filter = cfo < 1 ? `blur(${(1 - cfo) * 6}px)` : 'none';
    if (T > 5.52) ck.style.opacity = cfo;

    // cursor
    const [cx, cy] = path(CUR, T);
    const cs = clickScale(T, 0.85);
    const cu = $('cursor');
    cu.style.transform = `translate(${cx.toFixed(2)}px,${cy.toFixed(2)}px) scale(${cs.toFixed(3)})`;
    cu.style.visibility = T > 0.55 && T < 5.3 ? 'visible' : 'hidden';

    if (window.MM_EXTRA) window.MM_EXTRA(T, st);
  }

  // place every .t by its measured left edge (data-x) and baseline (data-b); Inter/Inter Tight baseline = top + 0.864*size at line-height 1
  function layoutText() {
    document.querySelectorAll('.t').forEach((el) => {
      const fs = parseFloat(getComputedStyle(el).fontSize);
      el.style.left = el.dataset.x + 'px';
      el.style.top = (parseFloat(el.dataset.b) - 0.952 * fs) + 'px';
    });
  }
  window.MM = { layoutText, render, S, clamp, lerp, mix3, rgb, easeOut, easeInOut, bez, standard, vis, fade, path, table, ORANGE, INK, INK2 };
})();
