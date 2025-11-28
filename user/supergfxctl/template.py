pkgname = "supergfxctl"
pkgver = "5.2.7"
pkgrel = 0
build_style = "cargo"
hostmakedepends = ["cargo-auditable", "pkgconf"]
makedepends = ["dinit-chimera", "dinit-dbus", "rust-std", "udev-devel"]
depends = ["lsof", "udev"]
pkgdesc = "Graphics switching utility for ASUS ROG laptops"
license = "MPL-2.0"
url = "https://gitlab.com/asus-linux/supergfxctl"
source = f"{url}/-/archive/{pkgver}/supergfxctl-{pkgver}.tar.gz"
sha256 = "bdd82f19094e11ede209830f62a2b408585b3994de800720ca23fb0a3dcd84a2"
# tests require hardware
options = ["!check"]


def post_install(self):
    self.install_file(
        "data/org.supergfxctl.Daemon.conf", "usr/share/dbus-1/system.d"
    )
    self.install_file(
        "data/90-nvidia-screen-G05.conf", "usr/share/X11/xorg.conf.d"
    )
    self.install_file(
        "data/90-supergfxd-nvidia-pm.rules", "usr/lib/udev/rules.d"
    )
    self.install_service("^/supergfxd", enable=True)
    self.install_file("^/envfile", "usr/share/supergfxctl")
    self.install_file("^/envfile", "etc/default", name="supergfxd")
    self.install_license("LICENSE")


@subpackage("supergfxctl-dinit")
def _(self):
    self.subdesc = "dinit service units"
    self.install_if = [self.parent, "dinit-chimera"]
    self.depends = [self.parent, "dinit-chimera", "dinit-dbus"]

    return ["usr/lib/dinit.d"]
