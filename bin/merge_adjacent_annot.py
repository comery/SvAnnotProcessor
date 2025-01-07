import sys
from icecream import ic
def merge_intervals(intervals):
    """Merges overlapping/adjacent intervals of the same type."""
    min_distance = 20
    merged = []
    if not intervals:
        return merged
    current = intervals[0]
    for interval in intervals[1:]:
        if interval[6] == current[6] and interval[4] - current[5] <= min_distance:
            current[5] = interval[5]
            current[7] = current[5] - current[4]
            current[8] = round(current[7] / (current[2] - current[1]), 5) if (current[2] - current[1]) != 0 else 0
        else:
            merged.append(current)
            current = interval
    merged.append(current)
    return merged

def filter_repeats(intervals):
    """Filters repeat annotations based on overlap with other types."""
    repeats = [interval for interval in intervals if interval[6] in ('Simple_repeat', 'other_repeat')]
    others = [interval for interval in intervals if interval[6] not in ('Simple_repeat', 'other_repeat')]
    filtered = []
    for repeat in repeats:
        overlapping = False
        for other in others:
            if repeat[0] == other[0] and max(repeat[4], other[4]) < min(repeat[5], other[5]):
                overlapping = True
                if repeat[4] < other[4]:
                    new_repeat = repeat[:4] + [repeat[4], other[4] - 1] + repeat[6:]
                    new_repeat[7] = new_repeat[5] - new_repeat[4]
                    new_repeat[8] = round(new_repeat[7] / (new_repeat[2] - new_repeat[1]), 5) if (new_repeat[2] - new_repeat[1]) != 0 else 0

                    filtered.append(new_repeat)
                if repeat[5] > other[5]:
                    new_repeat = repeat[:4] + [other[5] + 1, repeat[5]] + repeat[6:]
                    new_repeat[7] = new_repeat[5] - new_repeat[4]
                    new_repeat[8] = round(new_repeat[7] / (new_repeat[2] - new_repeat[1]), 5) if (new_repeat[2] - new_repeat[1]) != 0 else 0
                    filtered.append(new_repeat)
                break
        if not overlapping:
            filtered.append(repeat)
    filtered.extend(others)  # Add back the other intervals
    return filtered

def filter_by_length_and_coverage(intervals):
    """Filters and merges annotations based on length and coverage criteria."""
    filtered_data = []
    annotations = {}
    for interval in intervals:
        seq_name = interval[0]
        annotation_type = interval[6]
        length = interval[7]
        coverage = interval[8]

        if seq_name not in annotations:
            annotations[seq_name] = {}
        if annotation_type not in annotations[seq_name]:
            annotations[seq_name][annotation_type] = {"total_length": 0, "intervals": []}

        annotations[seq_name][annotation_type]["total_length"] += length
        annotations[seq_name][annotation_type]["intervals"].append(interval)


    final_output = {}  # Initialize final output here
    for seq_name, types in annotations.items():
        for annotation_type, data in types.items():
            total_length = data["total_length"]
            if total_length > 50:
                 # Max coverage selection logic (using the max coverage interval's coverage for all intervals belonging to the same annotation type within the same sequence)
                max_coverage = 0
                for interval in data["intervals"]:
                    max_coverage = max(max_coverage, interval[8])

                if max_coverage > 0.2:
                    key = f"{seq_name}_{annotation_type}"
                    if key not in final_output:
                        first_interval = data["intervals"][0]  #first interval of the annotation type
                        final_output[key] = {"seq_name": first_interval[0], "start": first_interval[1], "end": first_interval[2], "annotation_type": first_interval[6],
                                             "total_length": 0, "coverage": max_coverage}


                    final_output[key]["total_length"] += total_length #update the total length
    return list(final_output.values())




def process_annotations(file_path):

    try:
        with open(file_path, 'r') as f:
            data = [line.strip().split('\t') for line in f]
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return

    current_seq = None
    current_data = []

    for row in data:
        seq_name = row[0]
        row[1] = int(row[1])
        row[2] = int(row[2])
        row[4] = int(row[4])
        row[5] = int(row[5])
        row[7] = int(row[7])
        row[8] = float(row[8])

        if current_seq is None:
            current_seq = seq_name
            current_data.append(row)

        elif seq_name == current_seq:
            current_data.append(row)
        else:
            yield filter_by_length_and_coverage(filter_repeats(merge_intervals(current_data)))

            current_seq = seq_name
            current_data = [row]

    yield filter_by_length_and_coverage(filter_repeats(merge_intervals(current_data)))  # yield the last sequence


if __name__ == "__main__":
    file_path = sys.argv[1]
    for processed_seq in process_annotations(file_path):
        for output in processed_seq:
            print(f"{output['seq_name']}\t{output['start']}\t{output['end']}\t{output['annotation_type']}\t{output['total_length']}\t{output['coverage']}")
