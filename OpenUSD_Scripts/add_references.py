import pathlib

from pxr import Usd, Sdf


def ask_flatten() -> bool:
    while True:
        result = input("Do you want to execute flatten layers? 'yes' or 'no' [Y/N]: ").lower()
        if result in ['y', 'ye', 'yes']:
            return True
        elif result in ['n', 'no']:
            return False


def add_references(stage: Usd.Stage, base_file: pathlib.Path, referenced_dir: pathlib.Path, enable_flatten: bool) -> Sdf.Layer:
    referenced_dir_path = pathlib.Path(referenced_dir)
    referenced_files = {p.stem: p for p in referenced_dir_path.glob("*.usd")}

    print("Add Reference...")
    for prim in stage.Traverse():
        name = prim.GetPath().name
        if name in referenced_files:
            prim.SetTypeName("Xform")

            referenced_file = referenced_files[name]
            if referenced_file.is_relative_to(base_file):
                referenced_file = referenced_file.relative_to(base_file)
            reference_str = str(referenced_file).replace("\\", "/")

            prim.GetReferences().AddReference(reference_str)

    print(f"{len(referenced_files)} .usd files referenced.")

    if enable_flatten:
        print("Flatten...")
        root_layer = stage.Flatten()
    else:
        root_layer = stage.GetRootLayer()

    return root_layer


def main() -> None:
    base_file = input("Base usd file: ")

    stage = Usd.Stage.Open(base_file)
    print(f"Original animation range: {stage.GetStartTimeCode()} - {stage.GetEndTimeCode()}")

    referenced_dir = input("Referenced usd directory: ")
    dst_file = input("Destination usd file: ")
    enable_flatten = ask_flatten()

    base_file_path = pathlib.Path(base_file)
    root_layer = add_references(stage, base_file_path, pathlib.Path(referenced_dir), enable_flatten)

    root_layer.Export(dst_file)

    print("Done.", dst_file)


if __name__ == "__main__":
    main()
