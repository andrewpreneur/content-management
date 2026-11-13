---
name: components-library
description: Use Andrew's component library (andrewpreneur/andrews-components) to build videos faster: measured motion components, GSAP, Kokonut UI, 21st.dev components and video blocks, plus the video rules and a search tool. Use before building any new motion graphic, ad, explainer or animated scene.
---

# Components library

Repo: https://github.com/andrewpreneur/andrews-components (React + Vite + Tailwind + shadcn).
1. Clone it next to this repo (`git clone --depth 1 https://github.com/andrewpreneur/andrews-components ../andrews-components && cd ../andrews-components && npm install`).
2. Rules: `docs/video-rules.md` there (same rules as `saassuite-motion` + `docs/ai-video-rules.md` here).
3. Find: `npm run find -- <need>` (ours, GSAP recipes, 126 Kokonut components, saved 21st components).
4. Build a composition in `src/compositions/`, check with `npm run still`, render with `npm run shoot -- <id> <fmt> --audio mix.wav`.
5. 21st.dev MCP needs `API_KEY_21ST` in the environment (never commit it).
New reusable pieces go back into that repo with a catalog entry. Finished MP4s still go to Drive + Content HQ from here.
