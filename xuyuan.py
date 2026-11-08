#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import random
import sys

STATE_FILE = os.path.expanduser("~/.xuyuan.json")
DEFAULT_STATE = {"wishes": 0, "sunk": 0, "last": "", "history": []}

PROG = os.path.basename(sys.argv[0]) or "xy"
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
REASONS_FILE = os.path.join(BASE_DIR, "reasons.txt")

COIN = r"""
      ___
     /   \
    |  ●  |
     \___/
"""

FALLBACK_REASONS = [
    "池底今天不上班。",
    "愿望已读，不回。",
    "池子听懂了，但池子不想动。",
]

OTHER_WORDS = ("前任", "别人", "暗恋对象")
OVER_OPTIMISM = ("一定", "马上", "明天就", "这次真的")
FLAG_WORDS = ("再也不", "最后一次", "从明天起")


def load_reasons():
    reasons = []
    try:
        with open(REASONS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                reasons.append(line)
    except Exception:
        pass
    return reasons or FALLBACK_REASONS


REASONS = load_reasons()


def load_state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        state = DEFAULT_STATE.copy()
        for key in state:
            if key in data:
                state[key] = data[key]
        return state
    except Exception:
        return DEFAULT_STATE.copy()


def save_state(state):
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"池子漏水了，状态没存上：{e}")


def usage():
    print(f"""{PROG} —— 一个只收愿望、不办事的许愿池

用法：
  {PROG} "你的愿望"    投一枚硬币，许一个愿望
  {PROG} stats         查看池子统计
  {PROG} sink          查看最近沉底记录
  {PROG} reset         清空池子

别名：xy / xuyuan 完全等价，敲哪个都行。
理由库：reasons.txt，欢迎 PR 加沉底理由。
本项目不实现愿望。请勿期待。""")


def pick_reason(text, n):
    if any(w in text for w in OTHER_WORDS):
        return "检测到愿望涉及他人，已自动沉底。"
    if any(w in text for w in OVER_OPTIMISM):
        return "检测到过度乐观，已提前沉底。"
    if any(w in text for w in FLAG_WORDS):
        return "检测到 flag，已沉底并备案。"
    reason = random.choice(REASONS)
    try:
        return reason.format(n=n)
    except Exception:
        return reason


def make_wish(text):
    text = text.strip()
    if not text:
        print("池子不收空气。")
        return

    state = load_state()
    state["wishes"] += 1
    state["sunk"] += 1
    state["last"] = text
    reason = pick_reason(text, state["wishes"])
    state["history"].append({"text": text, "reason": reason})
    state["history"] = state["history"][-5:]
    save_state(state)

    print(COIN)
    print(f"愿望已受理：{text}")
    print(f"沉底理由：{reason}")
    print("愿望实现：0 个。")
    print(f"当前沉底硬币：{state['sunk']} 枚。")
    print(f"这是你沉底的第 {state['wishes']} 个愿望。")


def show_stats():
    state = load_state()
    last = state["last"] or "无"
    wishes = state["wishes"]
    if wishes >= 50:
        comment = "池子建议你接受现实，但池子不会帮你。"
    elif wishes >= 10:
        comment = "池子对你的坚持表示赞赏，并继续沉底。"
    else:
        comment = "池子表示情绪稳定。"
    print(f"""你已许愿 {wishes} 次。
硬币沉底 {state['sunk']} 枚。
愿望实现 0 个。
沉底率：100.0%
池子评价：{comment}
最近一个愿望：{last}（已沉底）""")


def show_sink():
    state = load_state()
    history = state.get("history", [])
    if not history:
        print("池底空空如也。")
        print("你还没许过愿，或者池子忘了。")
        return
    print("最近沉底记录：")
    for i, item in enumerate(history, 1):
        print(f"{i}. {item['text']}    理由：{item['reason']}")
    print(f"池底累计：{state['sunk']} 枚硬币，0 个愿望。")


def reset():
    save_state(DEFAULT_STATE.copy())
    print("池子已清空。")
    print("你的愿望没了，但本来也没用。")
    print("池底传来一声：下次别来了。")


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help", "help"):
        usage()
    elif args[0] == "stats":
        show_stats()
    elif args[0] == "sink":
        show_sink()
    elif args[0] == "reset":
        reset()
    else:
        make_wish(" ".join(args))


if __name__ == "__main__":
    main()
