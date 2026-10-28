def word_frequency_report(passage):
    allowed = set(" abcdefghijklmnopqrstuvwxyz0123456789")
    new_text = "".join(char if char in allowed else " " for char in passage.lower())
    passage_dict = {}
    for word in new_text.split():
        passage_dict[word] = passage_dict.get(word, 0) + 1

    sorted_items = sorted(passage_dict.items(), key=lambda x: (-x[1], x[0]))
    return "".join(f"{word}: {count}\n" for word, count in sorted_items)


message = "A word, if you please, if you please"

print(word_frequency_report(message))