import argparse
import jcl3

parser = argparse.ArgumentParser()
parser.add_argument(
    "-f",
    "--file",
    type=str,
    default="newArch.tar",
    help="name of file to create",
)
parser.add_argument("-k", "--keys", nargs="*")
args = parser.parse_args()

if __name__ == "__main__":
    archive = jcl3.Archive(args.file, set(args.keys))
    while not archive.done:
        archive.doMore()
    archive.close()
    # print(set(args.keys))
