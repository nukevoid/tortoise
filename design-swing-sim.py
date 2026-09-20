# -*- coding: utf-8 -*-
"""Offline model of the fixed-tempo flip swing.

The cadence must not depend on how far the shell is already swinging, so the
phase runs on its own clock at a constant rate and the amplitude is a
separate quantity that a well-timed press feeds.

A press scores by how well it aligns with the way the shell is already
travelling: alignment = side * cos(phase), which is +1 pressing with the
swing at its fastest, 0 at the turning points, -1 pressing straight into it.
"""
import math, random, sys

DT = 1/60.0

class Cfg:
    def __init__(s, period=1.10, gain=0.34, decay=0.70, reload=0.26, tip=1.05, expo=0.5):
        s.period, s.gain, s.decay, s.reload, s.tip = period, gain, decay, reload, tip
        s.expo = expo
        s.w = 2*math.pi/period

def run(cfg, press_fn, limit=25.0, seed=0):
    rng = random.Random(seed)
    phase, amp, reload_t, t, presses = 0.0, 0.12, 0.0, 0.0, 0
    while t < limit:
        phase = (phase + cfg.w*DT) % (2*math.pi)
        amp *= cfg.decay**DT
        reload_t = max(0.0, reload_t - DT)
        side = press_fn(t, phase, amp, rng)
        if side and reload_t <= 0:
            presses += 1
            reload_t = cfg.reload
            align = side * math.cos(phase)
            amp = max(0.02, amp + cfg.gain * align * abs(align)**cfg.expo)
        if amp >= cfg.tip:
            return t, presses
        t += DT
    return None, presses

def rhythm(cfg, offset=0.0, jitter=0.0):
    """A player keeping time by watching the shell: each press is aimed at
    the beat itself, not at the last press, so slop does not accumulate."""
    st = {'n': 0, 'side': -1, 'next': None}
    half = cfg.period/2
    def f(t, phase, amp, rng):
        if st['next'] is None:
            st['next'] = offset + (rng.uniform(-jitter, jitter) if jitter else 0)
        if t >= st['next']:
            st['n'] += 1
            st['next'] = offset + st['n']*half + (rng.uniform(-jitter, jitter) if jitter else 0)
            st['side'] *= -1
            return st['side']
        return 0
    return f

def mash(cfg, rate):
    st = {'next': 0.0, 'side': -1}
    def f(t, phase, amp, rng):
        if t >= st['next']:
            st['next'] = t + 1.0/rate
            st['side'] *= -1
            return st['side']
        return 0
    return f

def rand(cfg, rate):
    def f(t, phase, amp, rng):
        return rng.choice([-1, 1]) if rng.random() < rate*DT else 0
    return f

def hold(cfg):
    st = {'done': False}
    def f(t, phase, amp, rng):
        if not st['done']:
            st['done'] = True; return -1
        return 0
    return f

def report(cfg, name, mk, n=12):
    out = [run(cfg, mk(cfg), seed=s)[0] for s in range(n)]
    got = [x for x in out if x is not None]
    if not got:
        return '%-26s never' % name
    return '%-26s %4.2fs  worst %4.2fs  %d/%d' % (
        name, sum(got)/len(got), max(got), len(got), n)

def sweep(cfg):
    print('period %.2fs -> one press every %.2fs, gain %.2f, decay %.2f, reload %.2f'
          % (cfg.period, cfg.period/2, cfg.gain, cfg.decay, cfg.reload))
    for line in [
        report(cfg, 'perfect rhythm',       lambda c: rhythm(c)),
        report(cfg, 'rhythm +-60ms',        lambda c: rhythm(c, jitter=0.06)),
        report(cfg, 'rhythm +-120ms',       lambda c: rhythm(c, jitter=0.12)),
        report(cfg, 'rhythm, quarter off',  lambda c: rhythm(c, offset=c.period/4)),
        report(cfg, 'mashing 14/s',         lambda c: mash(c, 14)),
        report(cfg, 'mashing 8/s',          lambda c: mash(c, 8)),
        report(cfg, 'mashing 4/s',          lambda c: mash(c, 4)),
        report(cfg, 'random 3/s',           lambda c: rand(c, 3)),
        report(cfg, 'one press then wait',  lambda c: hold(c)),
    ]:
        print('  ' + line)
    print()

for gain, decay, expo in [(0.34,0.70,0.5),(0.30,0.70,0.5)]:
    sweep(Cfg(gain=gain, decay=decay, expo=expo))
