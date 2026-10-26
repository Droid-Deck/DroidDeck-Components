# DroidDeck Components

Prebuilt pieces that [DroidDeck](https://github.com/Droid-Deck/DroidDeck) downloads, and the
pipelines that build and publish them. Keeping them here keeps the app repository's releases to
the app itself.

## droiddeck-esync packs

Patched `ntdll.so` and `wineserver` pairs that add eventfd sync (droiddeck-esync) to stock Proton
11 builds, one pack per Proton release.

| Release | Contents |
| --- | --- |
| `droiddeck-esync-valve` | packs for Valve's Proton and Proton Experimental (ARM64) |
| `droiddeck-esync-ge` | packs for GE-Proton (aarch64) |
| `droiddeck-esync-cachyos` | packs for proton-cachyos (arm64) |
| `droiddeck-esync-index` | `index.json` and `index.json.sig` (signed), the apk bundles, `watch-state.json` |

The app reads the signed index and fetches only the pack built for the Proton release a user has
installed. A pack carries the sha256 of the stock binaries it replaces, so it is never applied
to another release. The apk ships the bundle that `tools/droiddeck-esync/release.env` in the app
repository pins by name and sha256.

- `droiddeck-esync/`: patch series, pack and index tools, flavor list, revocations, signing
  public key. [PATCHES.md](droiddeck-esync/PATCHES.md) explains the backends, matching, the build
  and publish steps, signing setup and revocation.
- `.github/workflows/watch-proton-releases.yml`: checks every 20 minutes for new Proton builds and
  starts the pack build when one appears.
- `.github/workflows/build-droiddeck-esync-packs.yml`: builds, smoke-tests and publishes packs, then
  signs a new index (environment `droiddeck-esync-signing`, `main` only).
- `tests/`: unit tests for the tools and workflows.

## VR module

`vr.tar.zst` holds what DroidDeck's VR features need beyond the apk: the SteamVR driver, Vulkan
layer and hand render models staged into the Linux runtime, the camera hand tracking and pose
models, the Luma Ultra base calibration, and the OpenCV and MediaPipe native libraries their
Java classes in the apk load. Users download it on request and can uninstall it.

| Release | Contents |
| --- | --- |
| `vr-rN` | `vr.tar.zst`, `vr.sha256` and `vr.files.txt` (every file with its sha256) |

`.github/workflows/build-vr.yml` builds `tools/vr/module` of DroidDeck at the given ref and
publishes it under a new tag; a published tag is never replaced. The apk pins one release by tag,
sha256 and size in `tools/vr/module/release.env` of the app repository.

## Linux components nightly

Nightly DXVK, VKD3D-Proton and FEX for the Linux Steam client, whose games run on glibc Protons,
all on one release that is kept up to date.

| Release | Contents |
| --- | --- |
| `linux-nightly` | `DD-dxvk-`, `DD-dxvk-arm64ec-`, `DD-dxvk-gplasync-`, `DD-vkd3d-proton-`, `DD-vkd3d-proton-arm64ec-` and `DD-FEXCore-<version>-nightly.wcp`, and `state.json` |

`<version>` is the last upstream tag (`3.1.1`) or the commits past it (`3.1.1+151`). The profile's
`versionName` follows the stable `-Linux` packages: `DD-3.1.1+151-nightly`,
`DD-3.1.1+151-arm64ec-nightly`, `DD-3.1.1+151-gplasync-nightly`, `DD-2610+54-nightly`. Packages are laid out as a Proton tree under
`files/lib/wine/` with profile type `DXVK-Linux`, `VKD3D-Linux` or `FEXCore-Linux`.

- `.github/workflows/watch-linux-nightly.yml`: every hour compares upstream with `state.json` and
  starts the build for the components that moved.
- `.github/workflows/linux-nightly.yml`: builds those components with the steps of
  [The412Banner/Nightlies](https://github.com/The412Banner/Nightlies)' all-in-one nightly (FEX's
  unixlibs against glibc), replaces their files on the release and rewrites its notes. If the
  gplasync patch no longer applies or builds on DXVK master, the previous gplasync file stays.
  Only `main` publishes. Helpers in `tools/linux-nightly/`.

## License

GPL-3.0, the same as DroidDeck. See [LICENSE](LICENSE). The patch series modifies Wine, which is
LGPL-2.1-or-later.

## Catalogs and mirrored releases

DroidDeck reads its package catalogs from this repository's `main`: `components.json` (Windows
components), `desktop.json` (desktop and emulator packages), `linuxfs.json` (the Linux runtime) and
`steam-seed.json` (the Steam seed). `fex.json` records the FEX build x86 programs run on (the app follows it
and installs it in every session) and `fex-rootfs.json` the x86-64 system it runs in (FEX-Emu's Ubuntu 24.04
rootfs, whose sha256 `droiddeck-steam-x64` pins). Every file they point at lives on a
release here, produced by a workflow in `.github/workflows/`:
`mirror-release.yml` brings an existing release in with every
asset checked against the catalog (and leaves `SHA256SUMS` + `MIRROR.md` naming the run),
`mirror-upstream.yml` does the same for a file its upstream publishes outside GitHub,
`build-fex.yml` builds FEX from DroidDeck's `tools/fex` and replaces it on the single `fex` release before
recording the new version, FEX release and source commit in `fex.json`, and `watch-fex.yml` starts it every
six hours when FEX has a newer release or `tools/fex` changed on DroidDeck's `main`,
`component-snapshots.yml` records what a Windows component's installer leaves behind,
`build-vr.yml` builds the VR module (above),
`build-desktop.yml`, `build-emulator-source.yml`, `mirror-appimages.yml` and `build-linuxfs.yml`
build the rest. Nothing on a release is uploaded by hand.
