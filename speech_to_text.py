import speech_recognition as sr
import re

def parse_message(text: str):
    """
    Heuristic parser:
    1. Find a command keyword (send message to / text / tell / message / etc).
    2. Take the remainder and split by separators (that, saying, :, , , -).
    3. If no separator, assume the first token is the recipient (support titles like Dr.).
    Returns (recipient, message) or (None, None) if nothing detected.
    """
    if not text:
        return None, None

    original = text.strip()
    lower = original.lower()

    # Try longer phrases first so we match the intended command
    keywords = [
        "i want you to send a message to",
        "please send a message to",
        "send a message to",
        "send message to",
        "please send to",
        "i want you to send to",
        "i want you to send",
        "send to",
        "send",
        "message to",
        "please send",
        "message",
        "text",
        "tell",
        "say to",
        "say",
        "sms",
        "email"
    ]

    start = None
    for kw in keywords:
        idx = lower.find(kw)
        if idx != -1:
            start = idx + len(kw)
            break

    if start is None:
        return None, None

    remainder = original[start:].strip()
    if not remainder:
        return None, None

    # Split by clear separators first
    sep_pattern = re.compile(r"\bthat\b|\bsaying\b|:|,|-{1,2}", re.IGNORECASE)
    parts = sep_pattern.split(remainder, maxsplit=1)
    if len(parts) == 2:
        candidate_recipient = parts[0].strip()
        message = parts[1].strip()
        if candidate_recipient.lower().startswith("to "):
            candidate_recipient = candidate_recipient[3:].strip()
        if candidate_recipient == "":
            # fallback: first token is recipient
            words = remainder.split()
            if len(words) == 1:
                return None, None
            return words[0].strip(), " ".join(words[1:]).strip()
        return candidate_recipient, message

    # No separator - assume first word is recipient (support titles like Dr.)
    words = remainder.split()
    if len(words) == 1:
        return words[0].strip(), ""  # recipient only, no message
    titles = {'mr', 'mrs', 'ms', 'miss', 'dr', 'prof', 'doctor'}
    if words[0].rstrip('.').lower() in titles and len(words) >= 2:
        recipient = words[0] + " " + words[1]
        message = " ".join(words[2:])
        return recipient.strip(), message.strip()
    recipient = words[0]
    message = " ".join(words[1:])
    return recipient.strip(), message.strip()


# Speech recognition setup
recognizer = sr.Recognizer()

# Tuning to reduce premature cut-off:
recognizer.energy_threshold = 300            # baseline sensitivity (tweak to your mic)
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 1.8             # seconds of silence before it stops listening
recognizer.phrase_threshold = 0.3            # minimum speech duration to consider valid

with sr.Microphone() as source:
    print("Listening... (speak; a longer pause ~1.8s will stop recording)")
    recognizer.adjust_for_ambient_noise(source, duration=1)  # calibrate for background noise
    audio = recognizer.listen(source, timeout=None, phrase_time_limit=None)

try:
    text = recognizer.recognize_google(audio)
    print(f"You said: {text}")

    recipient, message = parse_message(text)

    if recipient and message is not None:
        print(f"Recipient: {recipient}")
        print(f"Message: {message}")
    else:
        print("Couldn’t clearly parse recipient and message.")

except sr.UnknownValueError:
    print("Could not understand audio.")
except sr.RequestError as e:
    print(f"Could not request results; {e}")
