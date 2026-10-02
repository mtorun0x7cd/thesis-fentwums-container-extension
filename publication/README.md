<!--
SPDX-FileCopyrightText: 2026 Mert Torun
SPDX-License-Identifier: CC-BY-4.0
-->

# Version of record

This folder holds the Master's thesis "Design and Implementation of a Modular Architecture for the Transparent Integration of Containerized Execution Environments for Heterogeneous Open-Source Binaries in OneWare Studio" by Mert Torun (TH Köln, 2026) as it was deposited.

| File | Work | Record | Bytes | SHA-256 | Licence | Relation to the sources |
| --- | --- | --- | --- | --- | --- | --- |
| `Torun_Containerized_Execution_OneWare.pdf` | Master's thesis | ePublications TH Köln, document 3597, <https://doi.org/10.57683/EPUB-3597> | 557,042 | `f7cb839334f73d2df225a323d0d0473181055a6041cdbca8233f33a8f0c74f93` | CC BY 4.0, as the catalogue record states; the file itself prints no licence. The mark of TH Köln on the title page is excepted, see [`NOTICE`](../NOTICE) | The version of record, byte-identical with the file the catalogue record serves. The sources in [`thesis/`](../thesis/) at the tag `epub-3597` reproduce its text, not its bytes |

The deposited file differs from the thesis as submitted for examination on 2026-07-02 in that the official cover sheet (Deckblatt) that page i refers to and the author's matriculation number on the title page were removed and the faculty line on the title page was corrected; its text layer, unlike that of the submitted file, also gives the ligatures ffi and ffl as letters.

## Relation to the sources

The deposited file was typeset from LaTeX on 2026-07-02 and afterwards linearised, with its metadata rewritten, by a step that is not part of this repository; the sources therefore reproduce its text and not its bytes. Where the committed sources had diverged from the deposited text, they were reconciled with it in 2026: the third item of Section 7.3 and four hyphens in Chapter 6 (the three machine headings of Section 6.2.1 and "3-5x" in Section 6.5.4). A build of the tag sets the same words on every page; one paragraph, on p. 22 (PDF p. 37) in Section 3.2.2, breaks its lines differently, because the sources bind the citation that ends it to the preceding word with a tie, which the deposited file was typeset without. [`scripts/compare_pdf_text.py`](../scripts/compare_pdf_text.py) compares the text of a build with this file, page by page, and CI runs the comparison on every push:

```sh
make verify-deposit
```

After the tag `epub-3597`, the text of the thesis changes only through [`ERRATA.md`](../ERRATA.md); the sources and this file stay as they are.

## Verifying the file

### Without an account

1. In a clone of this repository, check the file against [`SHA256SUMS`](SHA256SUMS):

   ```sh
   cd publication
   sha256sum -c SHA256SUMS          # on macOS: shasum -a 256 -c SHA256SUMS
   ```

2. Hash the file the catalogue record serves and compare the result with `SHA256SUMS`:

   ```sh
   curl -sSfL -o deposited.pdf https://epb.bibl.th-koeln.de/files/3597/Torun_Containerized_Execution_OneWare.pdf
   sha256sum deposited.pdf
   ```

3. The release `epub-3597` carries the file and `SHA256SUMS` as assets. The public REST API reports a digest for each asset. Written in hexadecimal without any algorithm prefix, as the command below prints it, the digest of the PDF must equal its line in `SHA256SUMS`:

   ```sh
   curl -sSf https://api.github.com/repos/mtorun0x7cd/thesis-fentwums-container-extension/releases/tags/epub-3597 \
     | jq -r '.assets[] | "\(.digest | sub("^[^:]*:"; ""))  \(.name)"'
   ```

### With plain git

The record tag `epub-3597` carries the author's SSH signature. The public key is published at <https://api.github.com/users/mtorun0x7cd/ssh_signing_keys>; its fingerprint is `SHA256:h0XIy0K+hRkQ921LjtoKu/jSPvvlP0r4BiAMuyEPIrI`.

```sh
key=$(curl -sSf https://api.github.com/users/mtorun0x7cd/ssh_signing_keys | jq -r '.[0].key')
echo "$key" | ssh-keygen -lf -                    # shows the fingerprint above
echo "info@mtorun0x7cd.com $key" > allowed_signers
git -c gpg.ssh.allowedSignersFile=allowed_signers tag -v epub-3597
```

### With a GitHub account

```sh
gh release verify epub-3597 --repo mtorun0x7cd/thesis-fentwums-container-extension
```

The deposited PDF is untagged, that is, it has no structure for assistive technology, and it cannot change: corrections to the thesis are listed in [`ERRATA.md`](../ERRATA.md).
