---
title: "Mother CLAUDE: Clean Your Room and Eat Your Vegetables"
published: false
description: The whole Mother CLAUDE system in one metaphor — you built an AI that makes sure you do the things you already know you should do.
tags: ai, productivity, automation, developerexperience
series: Designing AI Teammates
canonical_url: https://github.com/Kobumura/mother-claude/blob/main/articles/devto/part6-clean-your-room.md
---

> **TL;DR**: You know you should write documentation. You know you should run quality checks. You know you should create handoffs. You just... don't always do it. Mother CLAUDE is the responsible one who makes sure you do the things you already know you should do.

*Who this is for: Anyone who's made it through this series and wants the whole thing in one memorable metaphor. Anyone who's ever known the right thing to do and not done it anyway.*

**Part 6 of the Designing AI Teammates series.** This is the wrap-up. Parts 1-5 covered the what and how. This one covers the why — and it turns out the why is embarrassingly simple.

---

[Frankie Cleary](https://www.linkedin.com/posts/frankie-cleary_yourmove-aiengineering-claudecode-activity-7424829014189604864-j_AF) recently wrote a great breakdown of how Claude Code actually works under the hood. His punchline: *"The model is the same. The harness is the product."* He's right. The intelligence isn't in the model — it's in the context, tools, and orchestration you wrap around it.

His call to action: **Skip the model. Build the harness.**

I commented: *"My harness is named Mother CLAUDE and she makes sure I clean my room weekly and eat all my vegetables daily."*

This article is what I mean by that.

---

## The Confession

I know I should write documentation. I know it helps future me. I know it helps the team. I know it's "best practice."

I also know I should floss daily and call my mother more often.

Knowing isn't the problem. *Doing* is the problem.

Every team I've worked with has a graveyard of good intentions:
- "I'll document this later" (they won't)
- "I'll add tests after the feature works" (they won't)
- "I'll clean up this code before merging" (they won't)
- "I'll write a proper handoff at the end of the session" (it's 5pm on Friday, they won't)

We're not lazy. We're human. We get tired. We get distracted. We have mani/pedis scheduled for 2:30 and wine to follow.

**The entire Mother CLAUDE system exists because no one on a team — including me — can be trusted to clean their room and eat their vegetables every single day.**

---

## The Parenting Metaphor

It was a joke when I wrote it. But it's also... exactly what's happening.

Think about what a good parent does:
- Establishes clear expectations ("here's how our house works")
- Creates accountability ("did you do your homework?")
- Reminds you so you don't have to remember ("don't forget your lunch")
- Checks your work ("did you actually clean, or just shove things under the bed?")
- Lets you push back ("you can tell me if you think this rule is unfair")

That's not a parenting philosophy. That's the Mother CLAUDE system:

| Parenting | Mother CLAUDE | Article |
|-----------|---------------|---------|
| "Here's how our house works" | Documentation structure | Part 1 |
| "Write down what you did today" | Session handoffs | Part 2 |
| "I'll remind you so you don't forget" | Automated hooks | Part 3 |
| "Did you actually clean your room?" | Quality checkpoints | Part 4 |
| "You can tell me when I'm wrong" | Permission Effect | Part 5 |

I didn't set out to build an AI parent. I set out to leverage the speed AI gives us without letting the chores slide — because you still have to clean your room before you can go out and play. The parenting metaphor emerged because **that's what "making sure important things happen" looks like.**

---

## Part 1: "Here's How Our House Works"

Every household has rules. Some are written (no shoes inside). Most are implicit (we don't talk about politics at dinner).

The problem with implicit rules: new people don't know them. They have to learn through awkward trial and error. Or they never learn, and everyone's quietly frustrated.

**Part 1** was about making the implicit explicit:

```markdown
## How This Project Works

- Backend: PHP 7.4+ with Composer
- Frontend: Bootstrap 5, Chart.js
- Database: Two databases (App on Heroku, Admin on RDS)
- Deploy: Push to main, GitHub Actions handles the rest
```

This isn't just for Claude. It's for anyone joining the project — human or AI. The documentation says "here's how our house works" so nobody has to guess.

**The parenting principle**: Clear expectations prevent confusion. Write them down once, reference them forever.

---

## Part 2: "Write Down What You Did Today"

When I was a kid, my mom would ask what I learned at school. I'd say "nothing" (I learned things). She'd ask what I did with my friends. I'd say "stuff" (we did specific things).

The information existed. I just didn't feel like extracting it.

**Part 2** was about capturing what happened before it disappeared:

```markdown
# Session Handoff - Feature Implementation

**Completed**: Added user authentication flow
**Decisions Made**: Chose JWT over sessions (stateless, scales better)
**Files Changed**: auth.php, middleware.php, login.vue
**Next Steps**: Add refresh token logic
**Open Questions**: Should tokens expire after 24h or 7d?
```

The handoff captures what happened while it's fresh. The next session (or the next developer) doesn't start from zero.

**The parenting principle**: "Write it down" isn't punishment. It's preservation. Today's context is tomorrow's foundation.

---

## Part 3: "I'll Remind You So You Don't Have to Remember"

The problem with "write down what you did" is that you have to remember to do it.

You finish a productive session. You're in the flow. You close the terminal. And... you forgot to write the handoff. Again.

Good parents don't rely on kids remembering. They build reminders into the routine. Backpack by the door. Lunch in the fridge. Alarm for soccer practice.

**Part 3** was about removing humans from the reminder loop:

```json
{
  "hooks": {
    "PreCompact": [{ "command": "python session_handoff.py" }],
    "SessionEnd": [{ "command": "python session_handoff.py" }],
    "SessionStart": [{ "command": "python session_start.py" }]
  }
}
```

Now handoffs happen automatically. Context loads automatically. I don't have to remember because the system remembers for me.

**The parenting principle**: The best reminders are invisible. If you have to remember to remember, you'll forget.

---

## Part 4: "Did You Actually Clean, or Just Shove Things Under the Bed?"

There's "clean your room" and there's *clean your room*.

Kids learn fast that closing the closet door hides a lot of mess. That making the bed covers a multitude of sins. That "I cleaned" can mean "I moved things around."

Parents learn to check.

**Part 4** was about checking the work, not just trusting that it happened:

```markdown
## Checkpoint Questions

- [ ] Single Responsibility: Does each function do ONE thing?
- [ ] No Magic Numbers: Are constants named?
- [ ] Error Handling: What happens when this fails?
- [ ] The Meta Question: Would a new developer understand this without explanation?
```

And crucially: **Claude initiates the check, not me.**

No one on a team can be trusted to remember quality checks at 2pm on a Friday. But Claude can. The documentation tells Claude it's responsible for asking. The team's job shifts from "remember to check" to "respond to the check."

**The parenting principle**: Trust but verify. And if you can't trust yourself to verify, delegate the verification.

---

## Part 5: "You Can Tell Me When I'm Wrong"

The best parents aren't dictators. They create space for pushback.

"I think that rule is unfair" should get a hearing, not a shutdown. Kids who can't disagree openly disagree covertly — or stop engaging entirely.

**Part 5** was about giving Claude permission to push back:

```markdown
## Collaboration Notes

- Dorothy appreciates questions and proactive suggestions
- You are a team member, not just a tool
- If my approach seems suboptimal, say so
```

The result: Claude started offering suggestions I didn't ask for. Flagging patterns worth documenting. Questioning decisions that seemed off.

Not because Claude suddenly got smarter. Because Claude got *permission*.

**The parenting principle**: Healthy relationships are bidirectional. The best collaborators — human or AI — are the ones who can tell you when you're wrong.

---

## What I Actually Built

Looking back at this series, here's what happened:

I didn't build a smarter AI. Claude is the same model everyone else uses.

I didn't build a complex system. It's markdown files and Python scripts. We built it for Claude, but the architecture works with any AI assistant.

**I built a responsible roommate for the team — one who doesn't let any of us skip the boring stuff.**

- Documentation? Mother CLAUDE knows the house rules and reminds the team of them.
- Handoffs? Mother CLAUDE captures them automatically so no one has to remember.
- Quality checks? Mother CLAUDE asks the questions we'd all skip at 2pm on Friday.
- Feedback? Mother CLAUDE tells us when something seems off.

The "intelligence" isn't in the model. It's in the structure that makes good behavior automatic and bad behavior harder.

And here's what people miss about AI productivity:

> **The tools aren't the bottleneck. Trust is.** You can generate code at incredible speed, but if you can't trust that documentation is current, tests are passing, and the last session's context carried forward — you spend all that saved time double-checking, fixing, and re-orienting. You're not faster. You're just making messes faster.

Mother CLAUDE is what lets us actually use the speed. The chores aren't a tax on productivity. They're what makes the productivity possible. Do your chores, and you can really go out and play.

---

## The Vegetables You're Not Eating

Here's the uncomfortable question: **What are you skipping?**

Every team has their vegetables — the things they know they should do but don't:

| The Vegetable | Why We Skip It | What Happens |
|---------------|----------------|--------------|
| Documentation | "I'll remember" | New team members ramp blind |
| Tests | "It works, I checked" | The next developer breaks it |
| Code review checklist | "I eyeballed it" | Bugs ship to production |
| Handoffs | "It's all in my head" | Context dies when people rotate |
| Onboarding docs | "They can ask me" | You become the bottleneck |

You don't need AI to eat your vegetables. You need a system that makes eating them automatic — or at least makes skipping them visible.

Mother CLAUDE is one implementation. The principle is universal: **if it matters, don't rely on willpower.**

---

## The Meta-Lesson

This whole series — five articles on documentation, handoffs, hooks, checkpoints, and permission — boils down to one insight:

> **Humans are unreliable. Systems are reliable. Build systems.**

Not because humans are bad. Because humans are human. We get tired. We get distracted. We have lives outside of code.

AI lets us deliver to the screen faster than ever. But speed without discipline is just a faster mess. The goal isn't to replace human judgment. It's to ensure the judgment actually gets applied — even when we're tired, even when we're rushing, even when we have wine waiting.

Mother CLAUDE doesn't make decisions for me. She makes sure I make them.

---

## Your Move

You don't need to adopt the whole system. Start with one vegetable:

1. **The easiest win**: Add a `CLAUDE.md` to your project with basic context. Even 20 lines helps.

2. **The biggest impact**: Set up automatic session handoffs. The hook script is in the repo.

3. **The mindset shift**: Add one line to your docs: "You are a team member, not just a tool. Suggest improvements."

Pick one. See what changes. Add another.

**The system doesn't have to be perfect. It just has to be better than relying on you to remember.**

---

## Thank You

This series started as internal documentation for a solo project. It became something bigger because people asked questions, shared what worked (and what didn't), and pushed back when things were unclear.

Special thanks to:
- Everyone who commented on the articles with real feedback
- The readers who actually tried the hooks and reported bugs
- Claude, for being a surprisingly good collaborator on writing about collaboration

If you've made it through all six parts: thank you for reading. I hope something here makes your work a little easier, your AI a little more useful, and your Fridays a little more guilt-free.

Now go eat your vegetables.

---

*This article was written collaboratively with Claude, who reminded me twice to add sections I was going to skip. The system works.*

---

## Resources

The complete Mother CLAUDE system is open source:

- **GitHub**: [github.com/Kobumura/mother-claude](https://github.com/Kobumura/mother-claude)
- **All articles**: `articles/devto/`
- **Hook scripts**: `hooks/`
- **Templates**: `templates/`

Fork it, adapt it, make it yours. And if you build something cool, let me know.

---

*Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Free to use and adapt with attribution to Dorothy J. Aubrey.*
