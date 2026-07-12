# LK LEGO PQC library — binary distribution

The testbed's post-quantum primitives (ML-DSA-87 / FIPS 204, ML-KEM-768 / FIPS 203)
are provided by the **LK LEGO** PQC platform, a production-grade C library developed
by Suzhou LangKong Post-Quantum Technology Co., Ltd.

These binaries are distributed **for replication of the paper's results only**.
They are proprietary and are **not** covered by the repository's research license.
Redistribution outside this artifact, reverse engineering, and commercial use are
not permitted.

## Contents

| Path | Platform | Status |
|---|---|---|
| `windows-x64/dllpqcpro.dll` | Windows x86-64 (MSVC v142, AVX2) | included |
| `linux-x64/libpqcpro_unix.so` | Linux x86-64 | included |

## Usage

- **Windows single-process runs**: the launch scripts already point the JVM at this
  directory via `-Dlego.lib.dir=<repo>/native/windows-x64`.
- **Docker runs**: the Dockerfile copies `native/linux-x64/libpqcpro_unix.so` from the
  repo-root build context; `docker compose build` works directly (the Dockerfile clears
  the ELF exec-stack flag automatically).

## Swapping the backend

The testbed talks to the library through a narrow, flat C ABI; the exported
symbols are visible in the binaries. A library exposing the same surface can
substitute it — protocol-level results do not depend on the specific backend,
only the absolute microbenchmark numbers do.
