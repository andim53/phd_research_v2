import os
import re

def get_struct_paths(base_dir, indices=None, prefix="struct_", ext=".xsf"):
    """
    Collects .xsf structure files in the given directory and filters them
    based on numeric indices found at the end of their filenames.

    Example filenames:
        struct_97_0.xsf  → index = 0
        struct_99_3.xsf  → index = 3
        struct_81_4.xsf  → index = 4

    Parameters:
        base_dir (str): Directory containing the .xsf structure files.
        indices (list of int, optional): List of indices to include.
                                         If None, all .xsf files are returned.
        prefix (str, optional): Filename prefix before the numeric parts. Default is "struct_".
        ext (str, optional): File extension. Default is ".xsf".

    Returns:
        list of str: Full paths to matching .xsf files.
    """
    struct_paths = []
    pattern = re.compile(rf"{re.escape(prefix)}.*_(\d+){re.escape(ext)}$")

    # Iterate through all files in the directory
    for fname in os.listdir(base_dir):
        if fname.endswith(ext):
            match = pattern.match(fname)
            if match:
                idx = int(match.group(1))
                # If indices not given, include all; otherwise, filter by index
                if indices is None or idx in indices:
                    struct_paths.append(os.path.join(base_dir, fname))

    # Sort paths by numeric index for convenience
    struct_paths.sort(key=lambda x: int(re.search(r"_(\d+)\.xsf$", x).group(1)))

    return struct_paths
