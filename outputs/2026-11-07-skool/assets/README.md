# Skool launch assets (Nov 7, 2026)

**Review page:** https://claude.ai/artifact/ToB5uro5p2Y2FJs9TtR8Tk (section "Launch assets")

Same look as the onboarding videos (navy, yellow "A" mark, Inter Tight, rebuilt Skool-style UI). Community name left as `{{COMMUNITY_NAME}}`. Nothing posted.

| file (`jpg/`, PNG masters in `png/`) | size | use |
|---|---|---|
| course-01-start-here | 1460x752 | Classroom cover: Start Here |
| course-02-foundations | 1460x752 | Classroom cover: Foundations (tools + who you help) |
| course-03-build-with-ai | 1460x752 | Classroom cover: Build with AI |
| course-04-saas-offers | 1460x752 | Classroom cover: SaaS Offers |
| course-05-getting-clients | 1460x752 | Classroom cover: Getting Clients |
| course-06-follow-up-delivery | 1460x752 | Classroom cover: Follow-up & Delivery |
| course-07-skills-prompts | 1460x752 | Classroom cover: Skills & Prompts library |
| course-08-coaching-replays | 1460x752 | Classroom cover: Coaching call replays |
| community-banner | 2168x1152 (1084x576 at 2x) | Community cover/banner |
| pinned-1-welcome | 1600x900 | Welcome post graphic |
| pinned-2-introduce-yourself | 1600x900 | Introduce yourself post graphic |
| pinned-3-how-to-ask | 1600x900 | How to ask a question post graphic |
| template-1-goal-this-week ... template-5-seven-days | 1080x1080 | Weekly goal / win / progress / shipped / 7-day post templates |

Text drafts: `posts.md` (welcome post, intro template, how-to-ask guidelines, template copy). Wording from the onboarding scripts.

Notes
- Example content inside the mockups (offer "AI Receptionist", prompt text, member initials, message copy) is illustrative.
- Banner size: 1084x576 is the usual Skool cover ratio; check it in Skool's settings preview, it may crop.
- Rebuild: `node render_assets.mjs [id ...]` (needs `../onboarding/build/fonts.css`, made by `../onboarding/make_fonts.py`). All JPGs are under 400 KB.
