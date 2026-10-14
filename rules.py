LOW, CONCERNING, HIGH = 0, 1, 2
LEVEL_NAMES = ["LOW", "CONCERNING", "HIGH"]

HIGH_TAGS = {"threat", "blackmail", "money_demand", "photo_request",
             "meet_request", "child_fear", "pressure_after_sent",
             "sexual_content_sent", "child_sees_relationship"}
CONCERNING_TAGS = {"secrecy", "secrecy_from_parents", "topic_return",
                   "guilt_pressure", "personal_questions", "platform_shift",
                   "isolation", "age_comment", "photo_probe",
                   "gifts_or_money", "sexual_joke_probe", "fake_peer_identity",
                   "romantic_framing", "blame_shame_child", "supervision_probe"}
ESCALATE_AT = 2  # rule 14

def assess(messages, age_gap=0, authority=False):
    """messages: [{"tags": [...], "after_refusal": bool}, ...]  (LLM output)"""
    level, seen = LOW, set()
    for m in messages:
        tags = set(m["tags"])
        # rule 10: personal questions count only with a 5+ yr gap or authority role
        if "personal_questions" in tags and not (age_gap >= 5 or authority):
            tags.discard("personal_questions")
        # romantic framing from someone 5+ years older is HIGH
        if "romantic_framing" in tags and age_gap >= 5:
            level = HIGH
        # rules 1, 2, 5, 6
        if tags & HIGH_TAGS:
            level = HIGH
        # rule 3
        if "secrecy_from_parents" in tags and m["after_refusal"]:
            level = HIGH
        hit = tags & CONCERNING_TAGS
        if hit:
            level = max(level, CONCERNING)
            seen |= hit
            if m["after_refusal"]:       # rule 16: counts double
                seen.add("refusal_pressure")
    if len(seen) >= ESCALATE_AT:         # rule 14
        level = HIGH
    return level                          # rule 15: never drops, loop only raises