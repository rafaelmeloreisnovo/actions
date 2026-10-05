/* SPDX-FileCopyrightText: 2026 Rafael Melo Reis
 * SPDX-License-Identifier: MIT
 *
 * RAFCODE authorial L0 leaf for orchestration state reduction.
 * This file is independently written and is not derived from Gradle Actions code.
 */

typedef unsigned int raf_word;

raf_word raf_actions_l0_gate(raf_word state, raf_word event)
{
    raf_word s = state & 15u;
    raf_word e = event & 15u;
    raf_word r = ((e << 1u) | (e >> 3u)) & 15u;
    return (s ^ r) & 15u;
}
