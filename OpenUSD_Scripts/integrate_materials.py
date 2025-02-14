from pxr import Usd, UsdShade

ROOT_MATERIALS_PATH = "/root/mtl"
MATERIAL_SCOPE_NAME = "mtl"


def integrate_materials(src_file: str, dst_file: str) -> None:
    stage = Usd.Stage.Open(src_file)

    root_mtl = stage.GetPrimAtPath(ROOT_MATERIALS_PATH)
    root_mtls: dict[str, Usd.Prim] = {p.GetName(): p for p in root_mtl.GetChildren()}

    editor = Usd.NamespaceEditor(stage)

    print("Re-binding materials...")
    for geom_prim in stage.TraverseAll():
        material_binding_api = UsdShade.MaterialBindingAPI(geom_prim)
        direct_binding = material_binding_api.GetDirectBinding()
        material_prim = direct_binding.GetMaterial()
        if not material_prim:
            continue

        name = material_prim.GetPath().name
        if name in root_mtls and material_prim.GetPath() == root_mtls[name].GetPath():
            continue

        if name not in root_mtls:
            new_path = f"{ROOT_MATERIALS_PATH}/{name}"
            editor.MovePrimAtPath(material_prim.GetPath(), new_path)
            editor.ApplyEdits()

            root_mtls[name] = stage.GetPrimAtPath(new_path)

        new_material = UsdShade.Material(root_mtls[name])
        material_binding_api.Bind(new_material)

    print("Removing unused materials...")
    for prim in list(stage.Traverse()):
        if prim.IsValid() and prim.GetName() == MATERIAL_SCOPE_NAME and str(prim.GetPath()) != ROOT_MATERIALS_PATH:
            editor.DeletePrimAtPath(prim.GetPath())
            editor.ApplyEdits()

    print("Saving...")
    stage.GetRootLayer().Export(dst_file)


def main() -> None:
    src_file = input("Source usd file: ")
    dst_file = input("Destination usd file: ")

    integrate_materials(src_file, dst_file)


if __name__ == "__main__":
    main()
