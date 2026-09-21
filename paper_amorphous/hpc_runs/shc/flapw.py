import re
import shutil
import subprocess
from pathlib import Path
from collections import defaultdict

from ase.calculators.calculator import FileIOCalculator


class FLAPW(FileIOCalculator):
    """
    FLAPW計算用のASEカスタムCalculator。

    Workflow
    --------
    1. lapwin作成
    2. SCF計算
       mpiexec ./pflapw

    3. SCF結果の読み込み
    4. FLcopy scf
    5. SOC用lapwin作成
    6. SOC計算
       mpiexec ./pflapw

    7. FLcopy soc
    8. opticsファイル準備
    9. xoptics計算
    10. FLclean

    Updates
    1.Add parameter in def__init__ "nprocs" 
    """

    implemented_properties = ["energy"]

    name = "flapw"

    def __init__(
        self,
        input_file="lapwin",
        output_file="lapwout",
        jspins=2,
        star_cutoff=9.8,
        pw_cutoff=3.9,
        kpts=(5, 5, 5),
        sockpts=(50, 50, 50),
        smearing=0.001,
        xc="gga",
        starting_state="AFM",
        maxiter=100,
        mixing="A",
        representation="SR",
        mpi=False,
        nprocs=8,
        lattice_scale=1.0,
        **kwargs,
    ):

        self.input_file = input_file
        self.output_file = output_file

        self.jspins = jspins
        self.star_cutoff = star_cutoff
        self.pw_cutoff = pw_cutoff

        self.kpts = kpts
        self.sockpts = sockpts

        self.smearing = smearing
        self.xc = xc
        self.starting_state = starting_state
        self.maxiter = maxiter
        self.mixing = mixing
        self.representation = representation

        self.mpi = mpi
        self.nprocs = nprocs
        self.lattice_scale = lattice_scale

        # ASE FileIOCalculator用のcommand
        if self.mpi:
            command = f"mpiexec -n {self.nprocs} ./pflapw"
        else:
            command = "./flapw"

        super().__init__(
            command=command,
            **kwargs,
        )

    # =========================================================================
    # 1. Input
    # =========================================================================

    def write_input(
        self,
        atoms,
        properties=None,
        system_changes=None,
    ):
        """
        lapwinを作成する。
        """

        super().write_input(
            atoms,
            properties,
            system_changes,
        )

        infile = Path(self.directory) / self.input_file

        self.write_lapwin(
            atoms,
            infile,
        )

    def write_lapwin(
        self,
        atoms,
        filename,
    ):
        """
        FLAPW用lapwinを作成する。
        """

        formula = atoms.get_chemical_formula()

        # Angstrom -> Bohr
        ANG_TO_BOHR = 1.889726125

        cell_bohr = atoms.cell.array * ANG_TO_BOHR

        symbols = atoms.get_chemical_symbols()

        frac_coords = atoms.get_scaled_positions()

        # 元素ごとに座標をまとめる
        coord_dict = defaultdict(list)

        for sym, pos in zip(
            symbols,
            frac_coords,
        ):
            coord_dict[sym].append(pos)

        species = sorted(
            coord_dict.keys()
        )

        # ---------------------------------------------------------------------
        # RMTテーブルを読み込む
        # ---------------------------------------------------------------------

        rmt_table = {}

        readme = Path("README_MT-default")

        if not readme.exists():

            raise FileNotFoundError(
                "README_MT-default was not found."
            )

        with open(readme) as h:

            for line in h:

                m = re.search(
                    r"element\('([A-Za-z ]+)'\s*,"
                    r"\s*\d+\s*,"
                    r"\s*\d+\s*,"
                    r"\s*(\d+)\s*,"
                    r"\s*([0-9.]+)",
                    line,
                )

                if m:

                    symbol = m.group(1).strip()

                    lmax = int(
                        m.group(2)
                    )

                    rmt = float(
                        m.group(3)
                    )

                    rmt_table[symbol] = {
                        "lmax": lmax,
                        "rmt": rmt,
                    }

        # ---------------------------------------------------------------------
        # lapwin書き込み
        # ---------------------------------------------------------------------

        with open(filename, "w") as f:

            f.write(
                f"Title: {formula}\n"
            )

            f.write(
                "Mode: bulk  auto                            "
                "!bulk/film auto/kpts/base\n"
            )

            # -----------------------------------------------------------------
            # Lattice vectors
            # -----------------------------------------------------------------

            f.write(
                "*** lattice vectors **********************\n"
            )

            f.write(
                f"{self.lattice_scale:.5f}\n"
            )

            for vec in cell_bohr:

                f.write(
                    f"{vec[0]:12.6f} "
                    f"{vec[1]:12.6f} "
                    f"{vec[2]:12.6f}\n"
                )

            # -----------------------------------------------------------------
            # Atomic coordinates
            # -----------------------------------------------------------------

            f.write(
                "*** atomic number cartesian or internal coordinates\n"
            )

            f.write(
                "set pos file:F, name:fconst_pos1.dat\n"
            )

            f.write(
                "internal\n"
            )

            for sym in species:

                positions = coord_dict[sym]

                x, y, z = positions[0]

                f.write(
                    f"{sym:<2} "
                    f"{x:12.8f} "
                    f"{y:12.8f} "
                    f"{z:12.8f}\n"
                )

                for pos in positions[1:]:

                    x, y, z = pos

                    f.write(
                        f"   "
                        f"{x:12.8f} "
                        f"{y:12.8f} "
                        f"{z:12.8f}\n"
                    )

            # -----------------------------------------------------------------
            # Space group
            # -----------------------------------------------------------------

            f.write(
                "*** SPACE GROUP ***************************\n"
            )

            f.write(
                f"Representation:{self.representation} ,"
                f"option:default              "
                f"!SR/ZR/FR/UR SR:default\n"
            )

            # -----------------------------------------------------------------
            # General options
            # -----------------------------------------------------------------

            f.write(
                "*** GENERAL OPTIONS ***********************\n"
            )

            general_options = [

                "Density of states:F, option:default\n",

                "Band structure:F, option:default\n",

                "Density plot:F, option:default\n",

                "Slice analysis:F, option:set\n",

                "Force calculation:F, option:default\n",

                "Geometry optimization:F, option:default\n",

                "Nudged elastic band:F, option:default\n",

                "Force constant calculation:F, option:default\n",

                "Electron-phonon coupling:F, option:set\n",

                "External E field:F, option:set\n",

                "External H field:F, option:set\n",

                "Jellium potential:F, option:set\n",

                "Electric field gradient:F, option:default\n",

                "L matrix calculation:F, option:default\n",

                "P matrix calculation:F, option:default\n",

                "J matrix calculation:F, option:default\n",

                "Second variational +U:F, option:set\n",

                "Second variational SOC:F, option:default\n",

                "Dispersion correction:F, option:default\n",

                "Magnetic dipole-dipole:F, option:default\n",

                "Noncollinear Magnetism:F, option:set\n",

                "Equi-density constraint:F, option:set\n",

            ]

            for line in general_options:

                f.write(line)

            # -----------------------------------------------------------------
            # Basis
            # -----------------------------------------------------------------

            f.write(
                "*** BASES *********************************\n"
            )

            f.write(
                f"star-function cut-off:{self.star_cutoff}\n"
            )

            f.write(
                f"jspins={self.jspins}\n"
            )

            f.write(
                "e_float:T, xo:T\n"
            )

            f.write(
                "nwin=1\n"
            )

            f.write(
                f"plane-wave cut off:{self.pw_cutoff}\n"
            )

            f.write(
                "number of states:0\n"
            )

            f.write(
                "lapw parameters:set\n"
            )

            for elem in species:

                if elem not in rmt_table:

                    raise KeyError(
                        f"RMT data for {elem} was not found "
                        f"in README_MT-default"
                    )

                rmt = rmt_table[elem]["rmt"]

                lmax = rmt_table[elem]["lmax"]

                f.write(
                    f"{elem:<2} "
                    f"rmt={rmt:.2f} "
                    f"lmax={lmax} "
                    f"0.\n"
                )

                f.write(
                    "                   0.\n"
                )

            # -----------------------------------------------------------------
            # K-points
            # -----------------------------------------------------------------

            f.write(
                "*** K-POINTS ******************************\n"
            )

            f.write(
                "k-point generator:S, option:default\n"
            )

            f.write(
                f"Smearing:G, parameter:{self.smearing}\n"
            )

            f.write(
                "Time-reversal symmetry:T\n"
            )

            f.write(
                "Division along internal axis "
                "(each window new line)\n"
            )

            f.write(
                f"  {self.kpts[0]}   "
                f"{self.kpts[1]}   "
                f"{self.kpts[2]}\n"
            )

            # -----------------------------------------------------------------
            # Mixing
            # -----------------------------------------------------------------

            f.write(
                "*** MIXING  OPTIONS ***********************\n"
            )

            f.write(
                f"(B)royden or (S)traight mixing "
                f"for density:{self.mixing}\n"
            )

            f.write(
                f"Maximum number of iterations:"
                f"{self.maxiter}  20\n"
            )

            f.write(
                "Mixing parameter:0.\n"
            )

            f.write(
                "Convergency: 0.\n"
            )

            # -----------------------------------------------------------------
            # Spin
            # -----------------------------------------------------------------

            f.write(
                "*** OPTIONS FOR SPIN-POLARIZED CASE *******\n"
            )

            f.write(
                "Spin-options:set\n"
            )

            f.write(
                "Initial spin polarization:T\n"
            )

            f.write(
                f"Starting state and values:"
                f"{self.starting_state}\n"
            )

            mag_init = {
                "Fe": 3.0,
                "Co": 3.0,
                "Ni": 2.0,
                "Mn": 4.0,
                "Cr": 3.0,
            }

            for sym in species:

                moment = mag_init.get(
                    sym,
                    0.0,
                )

                f.write(
                    f" {sym:<2} "
                    f"{moment:4.1f} "
                    f"   0.0 "
                    f"   0.0 "
                    f"   0.0\n"
                )

            f.write(
                "Mixing parameter: 0.\n"
            )

            # -----------------------------------------------------------------
            # Advanced settings
            # -----------------------------------------------------------------

            f.write(
                "*** ADVANCED SETTINGS *********************\n"
            )

            f.write(
                "Advanced setup:set\n"
            )

            f.write(
                "Output:redu\n"
            )

            f.write(
                "Check potential and density:F\n"
            )

            f.write(
                f"Exchange correlation:{self.xc}\n"
            )

            f.write(
                "frcor:F, ctail:F\n"
            )

            f.write(
                "*** END ***********************************\n"
            )

    # =========================================================================
    # 2. Calculation execution
    # =========================================================================

    def _run_pflapw(self):
        """
        MPI環境は外部で設定済みとして、
        pflapwを実行する。
        """

        if not self.mpi:

            subprocess.run(
                ["./flapw"],
                cwd=self.directory,
                check=True,
            )

            return

        subprocess.run(
            ["mpiexec", "./pflapw"],
            cwd=self.directory,
            check=True,
        )

    def run_flapw(self):
        """
        SCF計算を実行する。
        """

        self._run_pflapw()

    def execute(self):
        """
        SOC計算を実行する。
        """

        self._run_pflapw()

    # =========================================================================
    # 3. Result
    # =========================================================================

    def read_results(self):

        outfile = (
            Path(self.directory)
            / self.output_file
        )

        if not outfile.exists():

            raise FileNotFoundError(
                f"{outfile} was not found."
            )

        text = outfile.read_text(
            errors="ignore"
        )

        matches = re.findall(
            r"total energy for it=\s*\d+:\s*"
            r"([-0-9.Ee+]+)\s*htr",
            text,
            flags=re.IGNORECASE,
        )

        if not matches:

            raise RuntimeError(
                "Could not find total energy in lapwout."
            )

        energy_hartree = float(
            matches[-1]
        )

        HARTREE_TO_EV = 27.211386245988

        self.results["energy"] = (
            energy_hartree
            * HARTREE_TO_EV
        )

    # =========================================================================
    # 4. FLcopy / FLclean / FLrst
    # =========================================================================

    def copy_scf(self):

        subprocess.run(
            [
                "FLcopy",
                "scf",
            ],
            cwd=self.directory,
            check=True,
        )

        workdir = Path(
            self.directory
        )

        scfdir = workdir / "SCF"

        scfdir.mkdir(
            exist_ok=True
        )

        for f in list(workdir.iterdir()):

            if (
                f.is_file()
                and f.name.endswith("scf")
            ):

                shutil.move(
                    str(f),
                    str(scfdir / f.name),
                )

        return scfdir

    def copy_soc(self):

        subprocess.run(
            [
                "FLcopy",
                "soc",
            ],
            cwd=self.directory,
            check=True,
        )

        workdir = Path(
            self.directory
        )

        socdir = workdir / "SOC"

        socdir.mkdir(
            exist_ok=True
        )

        for f in list(workdir.iterdir()):

            if (
                f.is_file()
                and f.name.endswith("soc")
            ):

                shutil.move(
                    str(f),
                    str(socdir / f.name),
                )

        return socdir

    def restart_scf(self):

        subprocess.run(
            [
                "FLrst",
                "scf",
            ],
            cwd=self.directory,
            check=True,
        )

    def clean(self):
        """
        xoptics終了後にFLcleanを実行する。
        """

        subprocess.run(
            [
                "FLclean",
            ],
            cwd=self.directory,
            check=True,
        )

    # =========================================================================
    # 5. SOC
    # =========================================================================

    def prepare_soc_lapwin(self):

        lapwin = (
            Path(self.directory)
            / self.input_file
        )

        if not lapwin.exists():

            raise FileNotFoundError(
                f"{lapwin} was not found."
            )

        text = lapwin.read_text()

        # ---------------------------------------------------------------------
        # P matrix
        # ---------------------------------------------------------------------

        old_pmatrix = (
            "P matrix calculation:F, option:default"
        )

        new_pmatrix = (
            "P matrix calculation:T, option:set\n"
            "  valence-valence:T, if T set matrix type"
            "             !default:T\n"
            "    spin matrix:T"
            "                                      !default:F\n"
            "    orbital MT matrix:T"
            "                                !default:F\n"
            "    torque matrix:F"
            "                             !default:F\n"
            "    choose type:F, if T set species:"
            "                   !default:F\n"
            "  core-valence:F, if T set options"
        )

        if old_pmatrix not in text:

            raise RuntimeError(
                "P matrix calculation line was not found."
            )

        text = text.replace(
            old_pmatrix,
            new_pmatrix,
            1,
        )

        # ---------------------------------------------------------------------
        # SOC
        # ---------------------------------------------------------------------

        old_soc = (
            "Second variational SOC:F, option:default"
        )

        new_soc = (
            "Second variational SOC:T, option:set\n"
            "  Spin rotation:W"
            "                               !Wigner/Euler default: W\n"
            "    theta(alph)   phi(beta)    (gamm)"
            "            !degree\n"
            "    0.0          0.0\n"
            "  Scaling of strength:F, if T factor for spec:"
            "  !default:F\n"
            "  Pre-factor:F"
        )

        if old_soc not in text:

            raise RuntimeError(
                "Second variational SOC line was not found."
            )

        text = text.replace(
            old_soc,
            new_soc,
            1,
        )

        # ---------------------------------------------------------------------
        # K-point変更
        # ---------------------------------------------------------------------

        original_kpts = (
            f"  {self.kpts[0]}   "
            f"{self.kpts[1]}   "
            f"{self.kpts[2]}"
        )

        soc_kpts = (
            f"  {self.sockpts[0]}   "
            f"{self.sockpts[1]}   "
            f"{self.sockpts[2]}"
        )

        if original_kpts not in text:

            raise RuntimeError(
                "Original k-point division was not found."
            )

        text = text.replace(
            original_kpts,
            soc_kpts,
            1,
        )

        # ---------------------------------------------------------------------
        # 初期スピン分極をOFF
        # ---------------------------------------------------------------------

        old_spin = (
            "Initial spin polarization:T"
        )

        new_spin = (
            "Initial spin polarization:F"
        )

        if old_spin not in text:

            raise RuntimeError(
                "Initial spin polarization line was not found."
            )

        text = text.replace(
            old_spin,
            new_spin,
            1,
        )

        lapwin.write_text(
            text
        )

    # =========================================================================
    # 6. Optics
    # =========================================================================

    def prepare_optics(self):

        root = Path.cwd()

        optdir = root / "opt"

        workdir = Path(
            self.directory
        )

        if not optdir.exists():

            raise FileNotFoundError(
                f"{optdir} was not found."
            )

        for f in optdir.iterdir():

            if f.is_file():

                shutil.copy2(
                    f,
                    workdir / f.name,
                )

    def run_xoptics(self):

        subprocess.run(
            ["mpiexec", "./xoptics"],
            cwd=self.directory,
            check=True,
        )
