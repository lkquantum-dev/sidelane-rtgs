# Third-Party Notices

## JNA (Java Native Access) 5.14.0
- File: `sim/docker/lib/jna-5.14.0.jar`
- License: dual-licensed Apache License 2.0 / LGPL 2.1 (used here under Apache-2.0)
- https://github.com/java-native-access/jna

## ISO 20022 message schemas
- Files: `iso/pacs.008.001.09.xsd`, `iso/head.001.001.03.xsd`
  (bundled inside `sim/app/sidelane-sim.jar`)
- Source: ISO 20022 message definitions published at https://www.iso20022.org,
  redistributed here unmodified solely to enable schema validation in the testbed.
  ISO 20022 is a registered trademark of ISO.

## Eclipse Temurin (Docker base images)
- Image: `eclipse-temurin:21-jre` (pulled at build time,
  not redistributed in this repository).

## LK LEGO PQC platform (binary, not third-party but separately licensed)
- Files: `native/windows-x64/dllpqcpro.dll` (and `libpqcpro_unix.so` where provided)
- Proprietary; see `native/README.md`.
