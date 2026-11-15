#helper funcs to iterate frams and count lexical units across them
def get_frame_lu_counts(fn_corpus):
    frame_counts = []

    for frame in fn_corpus.frames():
        num_lus = len(frame.lexUnit)
        frame_counts.append((frame.name, frame.ID, num_lus))

    # Sort the list by lexical unit count in descending order
    frame_counts.sort(key=lambda item: item[2], reverse=True)
    return frame_counts

#2 frames with most lexical untis and how many
def exercise_3_2(fn_corpus):
    frame_counts = get_frame_lu_counts(fn_corpus)

    # Extract the top two frames with the highest number of lexical units
    top_two = frame_counts[:2]

    print("The two frames with the most lexical units are:")
    for rank, (frame_name, frame_id, count) in enumerate(top_two, start=1):
        print(f"  {rank}. {frame_name} (Frame ID: {frame_id}) -> {count} lexical units")

    print("\nTop 5 frames by lexical unit count (for reference):")
    for rank, (frame_name, frame_id, count) in enumerate(frame_counts[:5], start=1):
        print(f"  {rank}. {frame_name:<20} (ID: {frame_id:<4}) : {count} lexical units")

    return top_two
