pkgname = "fuse2"
pkgver = "2.9.9"
pkgrel = 0
build_style = "gnu_configure"
configure_args = ["--enable-lib", "--enable-util", "--disable-example"]
configure_env = {
    "MOUNT_FUSE_PATH": "/usr/bin",
    "UDEV_RULES_PATH": "/usr/lib/udev/rules.d",
    "INIT_D_PATH": "/etc/init.d",
}
hostmakedepends = ["automake", "libtool", "pkgconf", "gettext-devel"]
makedepends = ["linux-headers", "udev-devel"]
pkgdesc = "Filesystem in USErspace"
license = "GPL-2.0-or-later AND LGPL-2.1-or-later"
url = "https://github.com/libfuse/libfuse"
source = f"{url}/releases/download/fuse-{pkgver}/fuse-{pkgver}.tar.gz"
sha256 = "d0e69d5d608cc22ff4843791ad097f554dd32540ddc9bed7638cc6fea7c1b4b5"
file_modes = {"usr/bin/fusermount2": ("root", "root", 0o4755)}
# ld: error: default version symbol fuse_loop_mt@@FUSE_3.2 must be defined
# tests need examples and are useless in chroot
options = ["!lto", "!check"]


def post_patch(self):
    # modify source to use fusermount2
    self.do(
        "sed",
        "-i",
        "",
        's/"fusermount"/"fusermount2"/',
        "lib/mount.c",
        "util/mount.fuse.c",
    )


def post_install(self):
    # these are provided by fuse3 (or ignored)
    self.uninstall("etc/init.d")
    self.uninstall("usr/lib/udev")
    self.uninstall("dev")

    # stray header that might conflict with fuse3 or clutter include
    self.rm(self.destdir / "usr/include/fuse.h", force=True)

    # rename binaries for co-existence with fuse3
    self.mv(
        self.destdir / "usr/bin/fusermount",
        self.destdir / "usr/bin/fusermount2",
    )
    self.mv(
        self.destdir / "usr/bin/mount.fuse",
        self.destdir / "usr/bin/mount.fuse2",
    )

    # rename man pages
    self.mv(
        self.destdir / "usr/share/man/man1/fusermount.1",
        self.destdir / "usr/share/man/man1/fusermount2.1",
    )
    self.mv(
        self.destdir / "usr/share/man/man8/mount.fuse.8",
        self.destdir / "usr/share/man/man8/mount.fuse2.8",
    )


@subpackage("fuse2-devel")
def _(self):
    return self.default_devel()
