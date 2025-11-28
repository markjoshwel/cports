pkgname = "veracrypt"
pkgver = "1.26.24"
pkgrel = 0
archs = ["aarch64", "x86_64"]
build_style = "makefile"
hostmakedepends = ["yasm", "pkgconf"]
makedepends = [
    "fuse2-devel",
    "libsm-devel",
    "pcsc-lite-devel",
    "wxwidgets-devel",
]
depends = [
    "fuse2",
    "libsm",
    "lvm2-dm",
    "wxwidgets-gtk3",
]
pkgdesc = "Disk encryption utility derived from TrueCrypt"
license = "custom:TrueCrypt AND Apache-2.0"
url = "https://www.veracrypt.fr"
source = (
    f"https://launchpad.net/veracrypt/trunk/{pkgver}/+download/"
    f"VeraCrypt_{pkgver}_Source.tar.bz2"
)
sha256 = "7f5c20af429377ab56f7b52ca868936b9923d784f4606da9886c362978903e78"
# tests require GUI interaction and upstream offers no headless suite
options = ["!check", "!cross"]

make_build_env = {}


def _join_flags(*flags):
    return " ".join(flag for flag in flags if flag)


def init_build(self):
    self.make_build_env.update(
        {
            "PKG_CONFIG_PATH": "/usr/lib/pkgconfig",
            "TC_EXTRA_CFLAGS": _join_flags(self.get_cflags(shell=True)),
            "TC_EXTRA_CXXFLAGS": _join_flags(self.get_cxxflags(shell=True)),
            "TC_EXTRA_LFLAGS": _join_flags(
                "-ldl", self.get_ldflags(shell=True)
            ),
            "VC_FUSE_PACKAGE": "fuse",
        }
    )


def build(self):
    self.do(
        "make", f"-j{self.make_jobs}", env=self.make_build_env, wrksrc="src"
    )


def install(self):
    self.install_bin("src/Main/veracrypt")
    self.install_file(
        self.files_path / "veracrypt.desktop",
        "usr/share/applications",
    )
    self.install_file(
        "src/Resources/Icons/VeraCrypt-256x256.xpm",
        "usr/share/icons/hicolor/256x256/apps",
        name="veracrypt.xpm",
    )
    self.install_license("License.txt")
