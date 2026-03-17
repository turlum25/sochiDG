import os

os.system("clang -o sochiDG main.c -Xlinker -no_fixup_chains -mmacosx-version-min=10.13 -v")
os.system("clear")
