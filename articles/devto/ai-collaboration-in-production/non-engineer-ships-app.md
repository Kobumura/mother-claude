---
title: "The Monkey and the Engineer"
published: false
description: "Someone I know just published a real mobile app in the App Store. He works in software sales. The last code he wrote was for a COBOL final a billion years ago. He had no engineer helping him. Not even me."
tags: ai, productivity, mobile, developerexperience
series: AI Collaboration in Production
canonical_url: https://github.com/Kobumura/mother-claude/blob/master/articles/devto/ai-collaboration-in-production/non-engineer-ships-app.md
---

> **TL;DR**: Someone I know just published a real mobile app to the App Store and Google Play. He's in software sales. The last code he wrote was for a COBOL final a billion years ago. He had no engineer helping him. Not even me. Mother CLAUDE didn't turn him into an engineer -- it gave him a train and a mechanism to safely and responsibly lay his own tracks. All the steam was all him.

*Who this is for: Dreamers. People who've had an idea and didn't have the resources to make it a reality. There was a big brick wall built of time and money and resources and language-du-jour. Wall, meet train.*

---

> *Once upon a time there was an engineer*
> *Drove a locomotive both far and near*
> *Accompanied by a monkey who would sit on a stool*
> *Watching everything the engineer would move*

---

## Someone I Know Just Published a Mobile App

Not a prototype. Not a demo. Not "it works on my laptop." A real mobile app, available right now in the App Store and on Google Play, downloadable by anyone with a phone.

He's in software sales and the last time he wrote a line of code was for a COBOL final a billion years ago. (YES, FOR REAL!) Before this project, his most advanced "programming" in this millennium was of the vlookup variety; I'm sure it's impressive to his coworkers and I don't have the heart to tell him about INDEX(MATCH).

He had no engineer at the wheel. And he still hasn't written a line of code since 19-whenever.

He had me at the start, when I built the infrastructure. (I am an engineer. I did engineering things. Then I left.) He had Claude during every session, but Claude is a tool, not an engineer. The actual product work -- every session, every decision, every App Store submission -- was his.

---

## What I Did

Two empty repos. One for the React Native mobile app, one for the Node API server.

A Postgres database, dev and prod, credentials handed over.

A Node server, environment configured, sitting there waiting for code to run on it.

A side project of mine called LittlePipes, wired into his project to handle building, testing, signing, and deploying his app on every push to main.

Mother CLAUDE -- the documentation and handoff system I've been writing about for eight articles -- loaded into both repos so every Claude session would start with full context and would quietly but assuredly adhere to the same high standards I require of any engineer on my team: code style and linting, security practices, test coverage, migration safety, documentation discipline, and the kind of architectural consistency that keeps a project from rotting six months in.

I did not write a single line of his code. I did not make a single product decision. I built the engine, and I'd been the only one to ever drive this thing. For the first time, I handed over the keys and walked away.

---

## What He Did

He drove every session.

He decided what the app was. He decided what the screens looked like. He decided which retailer integrations to build first. He decided what should happen when a user opened the app for the second time, and the tenth time, and the hundredth. He decided when something wasn't good enough and pushed back. He decided when something was good enough and shipped it.

He paid for the Apple Developer account. He filled out the App Store metadata. He took the screenshots. He wrote the privacy policy. He answered Apple's review board's questions when they came back asking what one of his integrations did. He resubmitted when the first review didn't pass. He resubmitted again. He learned to curse at Apple as well as -- or better than -- anyone who has ever released to the App Store.

He shipped it.

Then he did it again on Google Play.

---

## What Claude Did

Everything else.

Claude wrote the code. Claude wrote the tests. Claude wired the APIs. Claude handled the build configs. Claude debugged what broke. Claude updated the documentation in `CLAUDE.md` so the next session inherited every decision. Claude flagged when his ideas were going to cause problems. Claude offered three options when there were three options worth considering, and recommended one when there was a clear best.

Claude is not an engineer. Claude is what happens when product intent, expressed in plain English, can be translated into working software without a person in the middle who needs to also understand how to write the software.

That distinction matters. An engineer is a human role with a career, a salary, judgment built up over years, and ownership of consequences. Claude has none of those things. Claude is a tool. A spectacularly capable one, but a tool.

The article's whole point is that he didn't need an engineer. He needed *the work an engineer would have done*, and Claude did that work, but no engineer was at the wheel. He was at the wheel. The wheel was responsive enough that someone whose last formal code was a COBOL final could drive it.

---

> *One day the engineer wanted a bite to eat*
> *He left the monkey sitting on the driver's seat*
> *The monkey pulled the throttle, locomotive jumped the gun*
> *Doing ninety miles an hour down the mainline run*

---

## Why This Isn't Vibe Coding

"Vibe coding" -- somebody opens an AI tool, types "build me an app," and posts a screenshot of the result -- is a great twitter thread and a terrible article. Vibe coding gets you a demo. Vibe coding does not get you a published mobile app.

Real published apps need:

- Repos that aren't full of half-finished scaffolding
- A database you can actually connect to, in dev and in prod
- A Node server standing up and receiving traffic
- A build pipeline that signs binaries, runs tests, and deploys
- A migration mechanism that updates schema without destroying production data
- Documentation the AI can read at session start so it doesn't forget what you decided last time
- Handoffs between sessions so a long project doesn't dissolve into contradictions
- Apple Developer account, App Store metadata, privacy policy, screenshots, review responses
- Google Play console, listing copy, content rating, store presence

Without all of that, even the best product thinker hits a wall in the first week.

He didn't hit that wall, because the wall wasn't there. The infrastructure was already standing when he started. Mother CLAUDE made every Claude session start oriented and end with the next one already prepared. LittlePipes turned every commit into a candidate build. The DB and server were there waiting for code.

So the only thing left for him to do was the part that had always been the actual hard part: deciding what to build, and seeing it through.

---

## What This Means

The phrase "non-engineer" is going to mean something different in five years. It's already starting to.

The old definition: someone who cannot build software because they don't know how to write code.

The new definition: someone whose product thinking isn't currently paired with the tooling that translates intent into code.

The second definition is a bottleneck you can fix. The first one was an identity.

If you've always wanted to build something and have believed for years that the code was beyond you -- the code is not beyond you. What you probably didn't have was a runway. The runway can be built. Mine took years, but the next person's won't, because the patterns are written down now and the AI tools are an order of magnitude better than they were even a year ago.

If you're an engineer watching AI tools get better and wondering what that means for your career -- the answer isn't that everyone becomes an engineer. It's that the people who understand infrastructure, systems, and how to lay runways become more valuable, not less. Somebody still has to build the rails.

---

> *Switch operator got the message in time*
> *Said there's a northbound train on the same mainline*
> *Open up the switch, I'm gonna let it through the hole*
> *'Cause the monkey's got the locomotive under control*

---

## The Core Insight

> **AI didn't make him a software engineer. It exposed that he always could have been one -- if the tracks had existed thirty years ago.**

He was never the person the "non-engineer" label suggested. He has product instincts sharper than most senior PMs I've worked with. His systems thinking was intact. His college COBOL didn't go anywhere; it just sat dormant, waiting for the rest of the toolchain to catch up.

Now the tracks are laid.

The wall is dead. Long live the train.

---

## But Things Aren't Always Awesome

I want to end this on the victory lap. I really do.

But I promised this series would be honest about what AI collaboration in production actually looks like. Sometimes the locomotive runs at ninety miles an hour, right on time, right on line.

Sometimes you've got Casey Jones at the throttle -- trouble ahead, trouble behind.

That's the next article: the time I let Claude SSH into a production server and watched the whole thing catch fire in slow motion.

---

*This article was written collaboratively with Claude, as part of the AI collaboration system it describes. SaveYour is a real app built on the Mother CLAUDE system.*

---

## Resources

- **Claude Code**: [claude.com/claude-code](https://claude.com/claude-code)
- **Mother CLAUDE**: [github.com/Kobumura/mother-claude](https://github.com/Kobumura/mother-claude)

---

*"The Monkey and the Engineer" -- words and music by Jesse Fuller (1961). Sung by Bob Weir on the Grateful Dead's* Reckoning *(1981), drawn from the acoustic sets at The Warfield and Radio City in fall 1980. 🤘 Weir carried the tune in his repertoire since 1964, back when the band was still Mother McCree's Uptown Jug Champions. Lyric excerpts © their respective rights holders, reproduced here as brief literary homage.*

---

*Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Free to use and adapt with attribution to Dorothy J. Aubrey.*

---

*For Bob Weir (1947–2026), who left us on January 10th. The train runs on.*
