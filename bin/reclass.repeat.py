import sys

def read_class(tsv):
    catelog = {}
    with open(tsv, 'r') as fh:
        for i in fh:
            tmp = i.strip().split("\t")
            catelog[tmp[0]] = tmp[1]
    return catelog


def main(class_file, annot_file):
    annot_class = read_class(class_file)
    with open(annot_file, 'r') as fh:
        for i in fh:
            tmp = i.strip().split("\t")
            if tmp[-1] in annot_class:
                tmp[-1] = annot_class[tmp[-1]]
            print("\t".join(tmp))

if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit(f"python3 {sys.argv[0]} class_file bed_file")
    else:
        main(sys.argv[1], sys.argv[2])
