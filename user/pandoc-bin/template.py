pkgname = "pandoc-bin"
pkgver = "3.8.2.1"
pkgrel = 0
archs = ["aarch64", "x86_64"]

pkgdesc = "Prebuilt pandoc CLI for conversion between documentation formats"
license = "GPL-2.0-or-later"
url = "https://pandoc.org"
provides = [f"pandoc={pkgver}", f"pandoc-cli={pkgver}"]
source = [
    f"https://github.com/jgm/pandoc/archive/{pkgver}.tar.gz",
]
sha256 = [
    "e3948e106026edbcef4e4d63f92554c814c779fa14696e635fb98e1279d4c175",
]
options = [
    "!check",
    "!strip",
]  # upstream binary with no runnable tests and already stripped artifacts

source_paths = ["pandoc-src"]

_bin_suffix = None
_bin_hash = None
_release_base = f"https://github.com/jgm/pandoc/releases/download/{pkgver}"

match self.profile().arch:
    case "x86_64":
        _bin_suffix = "amd64"
        _bin_hash = (
            "b362815e21d8ad3629c124aa92baf54558da086ad72374b4f6fdd97b9f3275b0"
        )
    case "aarch64":
        _bin_suffix = "arm64"
        _bin_hash = (
            "852e898c2490fa840ae75a8b6af8a6c9d6d63b77ef170c32ec3a17958464d929"
        )
    case _:
        pass

if _bin_suffix is None:
    broken = f"no upstream binary release for {self.profile().arch}"
else:
    source.append(f"{_release_base}/pandoc-{pkgver}-linux-{_bin_suffix}.tar.gz")
    sha256.append(_bin_hash)
    source_paths.append("pandoc-bin")


def install(self):
    src_root = self.srcdir / "pandoc-src"
    bin_root = self.srcdir / "pandoc-bin"
    bin_root_chroot = self.chroot_srcdir / "pandoc-bin"

    if not (bin_root / "bin" / "pandoc").exists():
        self.error("extracted binary tree missing pandoc executable")

    self.install_dir("usr/share/pandoc")
    self.cp(bin_root / "bin", self.destdir / "usr", recursive=True)

    share_dir = bin_root / "share"
    if share_dir.exists():
        self.cp(share_dir, self.destdir / "usr", recursive=True)

    pandoc_share = self.destdir / "usr/share/pandoc"
    for subdir in ("data", "citeproc"):
        src_dir = src_root / subdir
        if not src_dir.exists():
            self.error(f"missing '{subdir}' directory in source tree")
        self.cp(src_dir, pandoc_share, recursive=True)

    self.install_license(src_root / "COPYRIGHT")
    self.install_file(src_root / "COPYRIGHT", "usr/share/pandoc")
    self.install_file(src_root / "MANUAL.txt", "usr/share/pandoc")

    completion = self.do(
        str(bin_root_chroot / "bin" / "pandoc"),
        "--bash-completion",
        capture_output=True,
    ).stdout
    if isinstance(completion, str):
        completion = completion.encode()

    comp_src = self.cwd / "pandoc.bash"
    comp_src.write_bytes(completion)
    self.install_completion(
        str(comp_src.relative_to(self.cwd)), "bash", name="pandoc"
    )
    comp_src.unlink()
