pkgname = "ghostty"
pkgver = "1.2.3"
pkgrel = 0

_ghostty_zig = "0.14.0"
archs = ["aarch64", "x86_64"]
hostmakedepends = [
    "blueprint-compiler",
    "git",
    "pkgconf",
    "zip",
]
makedepends = [
    "fontconfig-devel",
    "gtk4-devel",
    "gtk4-layer-shell-devel",
    "libadwaita-devel",
    "libdrm-devel",
    "libinput-devel",
    "libseat-devel",
    "libxkbcommon-devel",
    "oniguruma",
    "oniguruma-devel",
    "wayland-devel",
    "wayland-protocols",
    "pandoc-bin",
]
depends = [
    self.with_pkgver("ghostty-shell-integration"),
    self.with_pkgver("ghostty-terminfo"),
    "libseat-seatd",
]
pkgdesc = "Fast, native, feature-rich terminal emulator"
license = "MIT"
url = "https://ghostty.org"
source = [
    f"https://release.files.ghostty.org/{pkgver}/ghostty-{pkgver}.tar.gz",
]

sha256 = [
    "559770fe9773161e93e3dd9177d916e27037d7f548edcf6186eabc571c0e520b",
]
options = ["!check", "!cross"]
source_paths = ["."]
hardening = ["!pie"]

match self.profile().arch:
    case "x86_64":
        _zig_dir = f"zig-linux-x86_64-{_ghostty_zig}"
        source.append(
            f"https://ziglang.org/download/{_ghostty_zig}/{_zig_dir}.tar.xz"
        )
        sha256.append(
            "473ec26806133cf4d1918caf1a410f8403a13d979726a9045b421b685031a982"
        )
        source_paths.append(_zig_dir)
    case "aarch64":
        _zig_dir = f"zig-linux-aarch64-{_ghostty_zig}"
        source.append(
            f"https://ziglang.org/download/{_ghostty_zig}/{_zig_dir}.tar.xz"
        )
        sha256.append(
            "ab64e3ea277f6fc5f3d723dcd95d9ce1ab282c8ed0f431b4de880d30df891e4f"
        )
        source_paths.append(_zig_dir)
    case _:
        broken = f"requires upstream Zig {_ghostty_zig} toolchain binary for {self.profile().arch}"


def _zig(self):
    return str(self.chroot_cwd / _zig_dir / "zig")


def _zig_cache(self):
    cache = self.statedir / "zig-cache"
    cache.mkdir(parents=True, exist_ok=True)
    return cache, self.chroot_statedir / "zig-cache"


def _zig_env(self):
    _, chroot_cache = _zig_cache(self)
    return {
        "ZIG_GLOBAL_CACHE_DIR": str(chroot_cache),
        "PATH": f"{self.chroot_cwd / _zig_dir}:/usr/bin",
    }


def _zig_build_args(self, install=False):
    _, chroot_cache = _zig_cache(self)
    args = [
        "build",
        "--summary",
        "all",
        "--system",
        str(chroot_cache / "p"),
        "-Doptimize=ReleaseFast",
        "-Dcpu=baseline",
        "-Dpie=false",
        "-Demit-themes=false",
        f"-Dversion-string={self.pkgver}-chimera{self.pkgrel}",
    ]
    if install:
        args.extend(["--prefix", "/usr"])
    return args


def _normalize_bash_completions(destdir):
    compdir = destdir / "usr/share/bash-completion/completions"
    if not compdir.is_dir():
        return
    for path in compdir.iterdir():
        if path.suffix != ".bash":
            continue
        target = path.with_suffix("")
        if target.exists():
            path.unlink()
        else:
            path.rename(target)


def prepare(self):
    env = _zig_env(self)
    rel_candidates = [
        "build.zig.zon.txt",
        "nix/build-support/build.zig.zon.txt",
    ]
    deps_rel = next(
        (rel for rel in rel_candidates if (self.cwd / rel).exists()), None
    )
    if not deps_rel:
        missing = ", ".join(
            str(self.chroot_cwd / rel) for rel in rel_candidates
        )
        raise FileNotFoundError(
            f"build.zig.zon.txt not found (checked: {missing})"
        )
    deps_host = self.cwd / deps_rel
    deps_chroot = self.chroot_cwd / deps_rel
    with open(deps_host, "r", encoding="utf-8") as depf:
        for url in depf:
            url = url.strip()
            if not url or url.startswith("#"):
                continue
            try:
                self.do(
                    _zig(self),
                    "fetch",
                    url,
                    env=env,
                    allow_network=True,
                )
            except Exception as exc:
                print(
                    f"warning: failed to fetch {url} listed in {deps_host.absolute()} ({exc})"
                )


def build(self):
    self.do(
        _zig(self),
        *_zig_build_args(self),
        env=_zig_env(self),
    )


def install(self):
    env = dict(_zig_env(self))
    env["DESTDIR"] = str(self.chroot_destdir)
    self.do(
        _zig(self),
        *_zig_build_args(self, install=True),
        env=env,
    )
    self.install_license("LICENSE")
    _normalize_bash_completions(self.destdir)
    _normalize_bash_completions(self.chroot_destdir)


def post_install(self):
    # upstream includes systemd user units that we do not package
    self.uninstall("usr/lib/systemd/user")


@subpackage("ghostty-shell-integration")
def _(self):
    self.subdesc = "Shell integration scripts"
    return ["usr/share/ghostty/shell-integration"]


@subpackage("ghostty-terminfo")
def _(self):
    self.subdesc = "Terminfo entries"
    return ["usr/share/terminfo"]
