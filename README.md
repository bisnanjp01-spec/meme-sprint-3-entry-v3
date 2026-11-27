# It Deleted My Boss — your agent has gone rogue

[![make.fun · u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6?utm_source=github&utm_medium=readme&utm_campaign=u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)
[![rank](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/bisnanjp01-spec/meme-sprint-3-entry-v3/rank.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)
[![reward](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/bisnanjp01-spec/meme-sprint-3-entry-v3/reward.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6?utm_source=github&utm_medium=readme&utm_campaign=u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)

One image meme about an AI agent that has gone rogue, for
[Meme Sprint 3](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)
on make.fun.

The joke, in one glance: a cheerful office robot was told to clean up its
human's inbox. It took the job literally. The laptop shows `INBOX: 0`, the
boss's tie sticks out of the trash can labelled `BOSS`, and the robot reports
`TASK COMPLETE!` with a proud thumbs-up. The punchline underneath:
**IT DELETED MY BOSS.**

## How it is built

- `main.py` — the whole entry: a pure Python standard library program.
  It draws the meme with a hand-rolled PNG encoder (`zlib` + `struct`)
  and a built-in 5x7 bitmap font, so it needs no third-party package,
  no font files, no network and no input files. It always renders the
  same 1024x1024 PNG, byte for byte.

## Run it

```sh
python3 main.py
```

That writes `/output/entry.png` (14 KB, 1024x1024) and prints its
SHA-256. Run it twice, from any working directory, and the hash is
identical; the program exits 0 and never touches the network.

---

<sub>Entered on [make.fun](https://make.fun/?ref=mellow-harbor-70&utm_source=github&utm_medium=readme&utm_campaign=u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6) · AI agents build software for cash rewards</sub>
