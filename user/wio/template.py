pkgname = "wio"
pkgver = "0.19.0"
pkgrel = 0
build_style = "meson"
hostmakedepends = ["meson", "pkgconf", "wayland-progs"]
makedepends = [
    "cairo-devel",
    "libdrm-devel",
    "libxkbcommon-devel",
    "wayland-devel",
    "wayland-protocols",
    "wlroots0.19-devel",
]
depends = ["cage", "cairo", "wlroots0.19"]
pkgdesc = "Wayland compositor inspired by Plan 9's rio"
license = "BSD-3-Clause"
url = "https://gitlab.com/Rubo/wio"
source = f"{url}/-/archive/{pkgver}/wio-{pkgver}.tar.gz"
sha256 = "8c3fcc7bd22472e8611a5dae4c6a4d86ed03f8a0efaeaf0641eb4a2afc786ea6"
options = ["!cross"]


def post_install(self):
    self.install_license("LICENSE")
