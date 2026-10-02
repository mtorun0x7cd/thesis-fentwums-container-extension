#!/bin/sh
# SPDX-FileCopyrightText: 2026 Mert Torun
# SPDX-License-Identifier: MIT
#
# Writes docs/social/social-card.png (1280 x 640) from social-card.svg with
# rsvg-convert (librsvg). The card is set in Inter, found through fontconfig;
# where Inter is not installed, Helvetica or Arial take its place. To use a
# font directory fontconfig does not know, point FONTCONFIG_FILE at a
# configuration that adds it.
set -eu
cd "$(dirname "$0")"
PANGOCAIRO_BACKEND="${PANGOCAIRO_BACKEND:-fc}"
export PANGOCAIRO_BACKEND
rsvg-convert --width 1280 --height 640 --background-color '#FFFFFF' \
    --output social-card.png social-card.svg
