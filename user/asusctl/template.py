pkgname = "asusctl"
pkgver = "6.1.21"
pkgrel = 0
build_style = "cargo"
make_build_args = [
    "--release",
    "--workspace",
    "--locked",
    "--exclude",
    "rog_simulators",
    # "--exclude",
    # "rog-control-center",
]
hostmakedepends = [
    "cargo-auditable",
    "cmake",
    "pkgconf",
]
makedepends = [
    "clang",
    "dinit-chimera",
    "dinit-dbus",
    "fontconfig-devel",
    "gettext-devel",
    "libayatana-appindicator-devel",
    "libinput-devel",
    "libseat-devel",
    "libseat-seatd",
    "libusb-devel",
    "openssl3-devel",
    "rust-std",
]
depends = [
    "gettext-libs",
    "libseat-seatd",
    "libusb",
    "udev",
]
pkgdesc = "Control daemon and CLI utilities for ASUS ROG laptops"
license = "MPL-2.0"
url = "https://asus-linux.org"
source = f"https://gitlab.com/asus-linux/asusctl/-/archive/{pkgver}/asusctl-{pkgver}.tar.gz"
sha256 = "fd860ca3e40c6945186a554cea4b7e9b9d32ed13d89bec1e524b1080c38b1a02"
# notest
options = ["!check", "!cross"]

make_build_env = {
    "RUSTFLAGS": "-C link-args=-lintl",
}
make_install_env = make_build_env


def _posixfy_makefile_coreutil_invocs(self):
    path = self.cwd / "Makefile"
    text = path.read_text()
    replacements = [
        (
            "VERSION := $(shell /usr/bin/grep -Pm1 'version = \"(\\d+.\\d+.\\d+.*)\"' Cargo.toml | cut -d'\"' -f2)",
            "VERSION := $(shell awk -F'\"' '/^version *=/ { print $$2; exit }' Cargo.toml)",
        ),
        (
            "SRC := Cargo.toml Cargo.lock Makefile $(shell find -type f -wholename '**/src/*.rs')",
            "SRC := Cargo.toml Cargo.lock Makefile",
        ),
        (
            'cd rog-anime/data && find "./anime" -exec',
            'cd rog-anime/data && find "./anime" -type f -exec',
        ),
    ]
    updated = text
    for old, new in replacements:
        updated = updated.replace(old, new)
    if updated != text:
        path.write_text(updated)


def build(self):
    self.do(
        "cp",
        self.chroot_srcdir / "Makefile",
        self.chroot_srcdir / "Makefile.bak",
    )
    _posixfy_makefile_coreutil_invocs(self)

    self.do(
        "make",
        f"ARGS={' '.join(make_build_args)}",
        f"DESTDIR={self.chroot_destdir}",
        "build",
        env={
            "RUSTUP_TOOLCHAIN": "stable",
            "CARGO_HOME": f"${self.chroot_srcdir}/cargo",
            "STRIP_BINARIES": "0",
            **self.make_build_env,
        },
    )


def install(self):
    self.do(
        "make",
        f"ARGS={' '.join(make_build_args)}",
        f"DESTDIR={self.chroot_destdir}",
        "install-asusctl",
        "install-asusd",
        "install-asusd_user",
        "install-rog_gui",
        "install-data-asusd",
        "install-data-asusd_user",
        "install-data-rog_gui",
        env={
            "RUSTUP_TOOLCHAIN": "stable",
            "CARGO_HOME": f"${self.chroot_srcdir}/cargo",
            "STRIP_BINARIES": "0",
            **self.make_build_env,
        },
    )


def post_install(self):
    self.uninstall("usr/lib/systemd")
    self.install_service("^/asusd", enable=True)
    self.install_service("^/asusd-user.user", enable=True)
    self.install_license("LICENSE")


@subpackage("asusctl-dinit")
def _(self):
    self.subdesc = "dinit service units"
    self.depends = [self.parent, "dinit-chimera", "dinit-dbus"]
    self.install_if = [self.parent, "dinit-chimera"]

    return [
        "usr/lib/dinit.d/asusd",
        "usr/lib/dinit.d/user/asusd-user",
    ]


@subpackage("rog-control-center")
def _(self):
    self.subdesc = "GUI companion"
    self.depends = [self.parent]

    return [
        "usr/bin/rog-control-center",
        "usr/share/applications/rog-control-center.desktop",
        "usr/share/icons/hicolor/512x512/apps/rog-control-center.png",
        "usr/share/icons/hicolor/scalable/status",
        "usr/share/rog-gui",
    ]
